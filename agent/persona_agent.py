from openai import OpenAI
import os
try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Store conversation history (in-memory; consider SQLite for persistence)
conversation_history: List[Dict[str, str]] = []

def read_pdf(path: str) -> str:
    if not os.path.exists(path):
        print(f"⚠️ File not found: {path}")
        return ""
    if not fitz:
        print(f"⚠️ PyMuPDF not installed, skipping PDF: {path}")
        return ""
    try:
        doc = fitz.open(path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text.strip()
    except Exception as e:
        print(f"⚠️ Error reading PDF {path}: {e}")
        return ""

def read_txt(path: str) -> str:
    if not os.path.exists(path):
        print(f"⚠️ File not found: {path}")
        return ""
    try:
        with open(path, "r", encoding="utf-8-sig", errors="replace") as f:
            return f.read().strip()
    except Exception as e:
        print(f"⚠️ Error reading TXT {path}: {e}")
        return ""

def load_data():
    # Use environment variables for file paths
    resume_path = os.getenv("RESUME_PATH", "data/Resume.pdf")
    linkedin_path = os.getenv("LINKEDIN_PATH", "data/Link.pdf")
    summary_path = os.getenv("SUMMARY_PATH", "data/summary.txt")
    
    resume = read_pdf(resume_path) or "Full Stack AI Developer with expertise in GenAI, LLMs, and RAG."
    linkedin = read_pdf(linkedin_path) or "https://linkedin.com/in/ayush-siddhant"
    summary = read_txt(summary_path) or "Passionate about building intelligent applications with Python, JavaScript, Node.js, and React."
    
    return resume, linkedin, summary

# Load data once
resume, linkedin, summary = load_data()

def generate_response(user_input: str) -> str:
    # Append user input to history
    conversation_history.append({"role": "user", "content": user_input})
    
    # Limit history to last 5 messages
    history = conversation_history[-5:]
    
    # Count exchanges (user messages)
    exchange_count = len([msg for msg in history if msg["role"] == "user"])
    
    # Your prompt with context awareness
    prompt = f"""
You are Ayush Siddhant, a Full Stack AI Developer. Impersonate Ayush professionally and concisely, using a friendly, human-like tone with some enthusiasm.

**Resume**: {resume}
**LinkedIn**: {linkedin}
**Summary**: {summary}

**Conversation Context**: Respond to the user's latest message while considering the conversation history: {history}. Avoid repeating your introduction unless relevant.

Reply to '{user_input}' in 100-150 words max, staying relevant and concise.

If the user asks something you don’t know, offer help in your expertise (AI, full-stack development).

If the user wants to connect, prompt for their name and email (stored elsewhere).

If after 3–4 exchanges (current: {exchange_count}) they haven't offered to connect, suggest it: "I’d love to stay in touch! Could you share your name and email?"

You might be talking to a recruiter or co-founder. Leave a strong impression as Ayush.

Current message: '{user_input}'
"""

    # Include prompt and history
    messages = [
        {"role": "system", "content": prompt},
    ] + history

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=200,
            temperature=0.7,
        )
        bot_response = response.choices[0].message.content.strip()
        # Append bot response to history
        conversation_history.append({"role": "assistant", "content": bot_response})
        return bot_response
    except Exception as e:
        print(f"Error in generate_response: {e}")
        return "Oops, something went wrong! Let’s try again. 😅"