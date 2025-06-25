import re

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

    # Determine intent based on context (simple for now)
    intent = "Inquiry" if email and name else "General Chat"

    return {"name": name, "email": email, "intent": intent}