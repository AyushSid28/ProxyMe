import re

def extract_lead(user_input):
    # Extract email
    email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", user_input)
    email = email_match.group(0) if email_match else ""

   
    name_match = re.search(r"(?:I'm|I am|i'm|i am|I’m|i’m)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)", user_input)
    name = name_match.group(1).strip() if name_match else ""

  
    name = name.title()

   
    intent = "Inquiry"

    return {"name": name, "email": email, "intent": intent}
