import re
import json
try:
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    import os
    import logging

    logger = logging.getLogger(__name__)

    llm = ChatOpenAI(
        api_key=os.getenv("OPENAI_API_KEY", "your-api-key-here"),
        temperature=0,
        model="gpt-4"
    )

    extraction_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert at extracting personal information from text. Given a user input, identify the user's name (prefer full names or capitalized words that seem like names) and email address (must be a valid email format like user@example.com). Return ONLY a valid JSON object with keys "name" and "email". If no information is found, return {"name": "", "email": ""}.
        Examples:
        - Input: "Hi, I'm Ayush, ayush@example.com" → {"name": "Ayush", "email": "ayush@example.com"}
        - Input: "Just chatting" → {"name": "", "email": ""}"""),
        ("user", "{input_text}")
    ])

except ImportError as e:
    logger.error(f"Failed to import langchain_openai: {e}. LLM fallback disabled.")
    llm = None
    extraction_prompt = None

def extract_lead(user_input):
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

    if (not name or not email) and llm is not None:
        logger.info(f"Regex failed, using LLM for: {user_input}")
        try:
            response = llm.invoke(extraction_prompt.format_messages(input_text=user_input))
            result = json.loads(response.content)  # Safely parse JSON
            name = result.get("name", "").title() if result.get("name") else name
            email = result.get("email", "") if result.get("email") else email
        except json.JSONDecodeError as e:
            logger.error(f"LLM returned invalid JSON: {e}, response: {response.content}")
        except Exception as e:
            logger.error(f"LLM extraction error: {e}")

    intent = "Inquiry" if email and name else "General Chat"
    return {"name": name, "email": email, "intent": intent}