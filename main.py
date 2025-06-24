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

app = FastAPI()

   # Configure templates and static files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"],  # Restrict to your domain in production
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )

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
       try:
           response = generate_response(user_input)
       except Exception as e:
           print(f"Error in generate_response: {e}")
           return {"response": "Error: Try again later"}

       conn = sqlite3.connect("data/leads.db")
       c = conn.cursor()

       # Store message
       c.execute("INSERT INTO message(input, response, timestamp) VALUES (?, ?, datetime('now'))",
                 (user_input, response))

       # Extract and store lead
       lead = extract_lead(user_input)
       if lead["name"] and lead["email"]:
           c.execute("INSERT INTO leads(name, email, intent, timestamp) VALUES (?, ?, ?, datetime('now'))",
                     (lead["name"], lead["email"], lead["intent"]))
           conn.commit()
           send_notification(lead["name"], lead["email"], lead["intent"])

       # Optional: Evaluate the response
       if os.getenv("USE_EVALUATOR", "false").lower() == "true":
           eval_score = evaluate_response(user_input, response)
           with open("data/eval_log.txt", "a") as f:
               f.write(f"Input: {user_input}, Response: {response}, Score: {eval_score}\n")

       conn.commit()
       conn.close()
       return {"response": response}