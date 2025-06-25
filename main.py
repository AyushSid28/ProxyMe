from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from agent.persona_agent import generate_response
from collector.lead_collector import extract_lead
from collector.push_notify import send_notification
from agent.evaluator import evaluate_response
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import os
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store (keyed by client IP for simplicity)
session_leads = defaultdict(lambda: {"name": "", "email": ""})

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect("data/leads.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            intent TEXT,
            timestamp TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS message (
            id INTEGER PRIMARY KEY,
            input TEXT,
            response TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html.j2", {"request": request, "apiUrl": "/"})

@app.post("/")
async def chat(request: Request):
    data = await request.json()
    user_input = data.get("input", "")
    client_ip = request.client.host  # Simple session ID using IP
    logger.info(f"Received input from {client_ip}: {user_input}")
    try:
        response = generate_response(user_input)
    except Exception as e:
        logger.error(f"generate_response error: {e}")
        return {"response": "Error: Try again later"}

    conn = sqlite3.connect("data/leads.db")
    c = conn.cursor()

    c.execute("INSERT INTO message(input, response, timestamp) VALUES (?, ?, datetime('now'))",
              (user_input, response))
    logger.info("Message stored")

    # Extract lead from current input
    lead = extract_lead(user_input)
    logger.debug(f"Extracted lead from input: {lead}")

    # Update session lead with current input
    session_leads[client_ip]["name"] = lead["name"] if lead["name"] else session_leads[client_ip]["name"]
    session_leads[client_ip]["email"] = lead["email"] if lead["email"] else session_leads[client_ip]["email"]

    # Check if we have a complete lead from session data
    if session_leads[client_ip]["name"] and session_leads[client_ip]["email"]:
        c.execute("INSERT INTO leads(name, email, intent, timestamp) VALUES (?, ?, ?, datetime('now'))",
                  (session_leads[client_ip]["name"], session_leads[client_ip]["email"], "Inquiry"))
        conn.commit()
        logger.info(f"Lead detected from session {client_ip}: {session_leads[client_ip]['name']}, {session_leads[client_ip]['email']}")
        send_notification(session_leads[client_ip]["name"], session_leads[client_ip]["email"], "Inquiry")
        logger.info("Notification attempt completed")
    else:
        logger.debug(f"Partial lead in session {client_ip}: {session_leads[client_ip]}")

    if os.getenv("USE_EVALUATOR", "false").lower() == "true":
        eval_score = evaluate_response(user_input, response)
        with open("data/eval_log.txt", "a") as f:
            f.write(f"Input: {user_input}, Response: {response}, Score: {eval_score}\n")

    conn.commit()
    conn.close()
    return {"response": response}

@app.get("/test-notification")
async def test_notification():
    from collector.push_notify import send_notification
    logger.info("Testing Pushover notification")
    send_notification("Test User", "test@example.com", "Test Intent")
    return {"message": "Notification test triggered"}