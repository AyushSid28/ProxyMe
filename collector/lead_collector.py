import re
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import os
import logging

logger = logging.getLogger(__name__)

# Initialize LLM (reuse existing setup or configure here)
llm = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY", "your-api-key-here"),  # Ensure this is set in Render env
    temperature=0,
    model="gpt-4"
)

# LLM prompt for extracting name and email
extraction_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert at extracting personal information from text. Given a user input, identify and extract the following:
    - The user's name (if present, prefer full names or capitalized words that seem like names).
    - The user's email address (if present, must be a valid email format).
    Return the result as a JSON object with keys "name" and "email". If no information is found, return empty strings for both.
    Example:
    Input: "Hi, I'm Ayush, ayush@example.com, need help!"
    Output: {"name": "Ayush", "email": "ayush@example.com"}
    Input: "Just chatting here"
    Output: {"name": "", "email": ""}"""),
    ("user", "{input_text}")
])

def extract_lead(user_input):
    # Initial regex-based extraction
    email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", user_input)
    email = email_match.group(0) if email_match else ""

    name_patterns = [
        r"(?:name is|my name is|I’m|I am|i'm|i am|I’m|i’m)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
        r"(?:name|my name)\s*:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
        r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b(?=\s*[,;]\s*[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"
    ]
    name = ""
    for pattern in name_patterns:
        name_match = re.search(pattern, user_input)
        if name_match:
            name = name_match.group(1).strip()
            break
    
    name = name.title() if name else ""

    # If regex fails to find both name and email, use LLM fallback
    if not name or not email:
        logger.info(f"Regex failed to extract lead, using LLM fallback for: {user_input}")
        try:
            response = llm.invoke(extraction_prompt.format_messages(input_text=user_input))
            result = eval(response.content)  # Assuming LLM returns a stringified JSON
            name = result.get("name", "").title() if result.get("name") else name
            email = result.get("email", "") if result.get("email") else email
        except Exception as e:
            logger.error(f"LLM fallback failed: {e}")
            pass  # Fall back to regex results

    intent = "Inquiry" if email and name else "General Chat"

    return {"name": name, "email": email, "intent": intent}