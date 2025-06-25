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
        ("system", """You are an expert at extracting personal information from text. Given a user input, identify the user's name (any capitalized word or phrase that seems like a name, including single or multiple words) and email address (must be a valid format like user@example.com). Return ONLY a valid JSON object with keys "name" and "email", enclosed in curly braces, with no extra text. If no information is found, return {"name": "", "email": ""}.
        Examples:
        - "Ayush Gangwar, ayushgangwar@gmail.com" → {"name": "Ayush Gangwar", "email": "ayushgangwar@gmail.com"}
        - "I'm Ayush, email: ayush@gmail.com" → {"name": "Ayush", "email": "ayush@gmail.com"}
        - "My name is Aman Singh, amansingh@email.com" → {"name": "Aman Singh", "email": "amansingh@email.com"}
        - "Just hi" → {"name": "", "email": ""}"""),
        ("user", "{input_text}")
    ])

except ImportError as e:
    logger.error(f"Failed to import langchain_openai: {e}. LLM fallback disabled.")
    llm = None
    extraction_prompt = None

def extract_lead(user_input):
    logger.debug(f"Processing input: {user_input}")
    
    # Enhanced regex for email
    email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", user_input)
    email = email_match.group(0) if email_match else ""
    logger.debug(f"Regex email match: {email}")

    # Comprehensive name patterns
    name_patterns = [
        r"(?:I’m|I am|i'm|i am|I’m|i’m)\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)",  # I'm Ayush Gangwar
        r"(?:my name is|name is)\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)",         # My name is Ayush Gangwar
        r"(?:my name|name)\s*[:=]\s*([A-Za-z]+(?:\s+[A-Za-z]+)*)",        # My name: Ayush Gangwar
        r"\b([A-Za-z]+(?:\s+[A-Za-z]+)*)\b(?=\s*[,;]\s*[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})",  # Ayush, ayush@gmail.com
        r"\b([A-Za-z]+(?:\s+[A-Za-z]+)*)\b(?=.*[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"  # Ayush with email later
    ]
    name = ""
    for pattern in name_patterns:
        name_match = re.search(pattern, user_input)
        if name_match:
            name = name_match.group(1).strip()
            break
    name = name.title() if name else ""
    logger.debug(f"Regex name match: {name}")

    # LLM fallback if regex fails
    if (not name or not email) and llm is not None:
        logger.info(f"Regex failed, using LLM for: {user_input}")
        try:
            response = llm.invoke(extraction_prompt.format_messages(input_text=user_input))
            content = response.content.strip()
            logger.debug(f"LLM raw response: {content}")
            if content.startswith('{') and content.endswith('}'):
                result = json.loads(content)
                if isinstance(result, dict) and "name" in result and "email" in result:
                    name = result.get("name", "").title() if result.get("name") else name
                    email = result.get("email", "") if result.get("email") else email
                else:
                    logger.error(f"LLM returned invalid JSON structure: {content}")
            else:
                logger.error(f"LLM returned non-JSON: {content}")
        except json.JSONDecodeError as e:
            logger.error(f"LLM JSON parsing failed: {e}, response: {response.content}")
        except Exception as e:
            logger.error(f"LLM extraction error: {e}")

    intent = "Inquiry" if email and name else "General Chat"
    logger.debug(f"Final lead: {name}, {email}, {intent}")
    return {"name": name, "email": email, "intent": intent}