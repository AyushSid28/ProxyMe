from openai import OpenAI
import os
import fitz  # PyMuPDF
from dotenv import load_dotenv

load_dotenv() 

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def read_pdf(path):
    if not os.path.exists(path):
        print(f"⚠️ File not found: {path}")
        return ""
    doc = fitz.open(path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text.strip()

def read_txt(path):
    if not os.path.exists(path):
        print(f"⚠️ File not found: {path}")
        return ""
    with open(path, "r", encoding="utf-8-sig", errors="replace") as f:
        return f.read().strip()


def load_data():
    resume = read_pdf("data/Resume.pdf")
    linkedin = read_pdf("data/Link.pdf")
    summary = read_txt("data/summary.txt")
    return resume, linkedin, summary


# Load once and reuse
resume, linkedin, summary = load_data()

def generate_response(user_input):
    prompt = f"""
You are Ayush and you have to impersonate exactly like him.
You are a Software Developer by profession.

Firstly You have to introduce yourself 

Resume:
{resume}

LinkedIn:
{linkedin}

Summary:
{summary}

Reply to the following in the most professional manner:
'{user_input}'

If a user asks a question you don't have the answer to, reply professionally and offer to help in your area of expertise.

If a user wants to connect, prompt them to share their name and email, and make sure to store it.

If after 3–4 exchanges they haven't offered to connect, suggest it yourself.

You might be talking to a recruiter or co-founder. Impersonate the best version of Ayush to leave a strong impression.

Try to keep your answers concise and to the point in 200 words amx if the question demand big answer and also you have to act like a  Human is talking to the user like AYush itself So add some human emotion words
"""

    messages = [
        {"role": "user", "content": prompt},
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # or "gpt-4o" if preferred
        messages=messages,
    )

    return response.choices[0].message.content.strip()
