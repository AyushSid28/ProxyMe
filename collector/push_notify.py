import requests
import os
import logging

logger = logging.getLogger(__name__)

def send_notification(name: str, email: str, intent: str):
    api_token = os.getenv("PUSHOVER_API_TOKEN")
    user_key = os.getenv("PUSHOVER_USER_KEY")
    if not api_token or not user_key:
        logger.error("Pushover credentials not found")
        return

    payload = {
        "token": api_token,
        "user": user_key,
        "message": f"{name}, ({email}) - {intent}"
    }

    try:
        response = requests.post("https://api.pushover.net/1/messages.json", data=payload, timeout=10)
        response.raise_for_status()
        logger.info(f"Pushover notification sent for {name}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Pushover notification failed: {e}, Response: {getattr(response, 'text', 'No response')}")