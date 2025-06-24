import requests
import os

def send_notification(name,email,intent):
    payload={
        "token":os.getenv("PUSHOVER_API_TOKEN"),
        "user":os.getenv("PUSHOVER_USER_KEY"),
        "message":f"{name},({email})-{intent}"
    }

    requests.post("https://api.pushover.net/1/messages.json",data=payload)

    