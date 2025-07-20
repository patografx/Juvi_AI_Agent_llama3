import requests
import ollama
import os
from dotenv import load_dotenv

load_dotenv() # Loads variables from .env file
TOKEN = os.getenv("TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"
CHAT_ID = os.getenv("CHAT_ID")
offset = None

def send_message(text):
    url = f"{BASE_URL}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text
    }
    response = requests.post(url, json=payload)
    print(response.json())
    return response.json()
    

def get_latest_message():
    global offset
    url = f"{BASE_URL}/getUpdates?timeout=100"
    if offset:
        url += f"&offset={offset + 1}"

    response = requests.get(url).json()
    updates = response.get("result", [])
    if not updates:
        return None

    latest = updates[-1]
    offset = latest["update_id"]

    message = latest.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text")

    return (chat_id, text, message) if chat_id else None

# Poll for new messages continuously
while True:
    result = get_latest_message()
    if result:
        chat_id, text, message = result
        print(f"Received from {chat_id}: {text}")

        response = ollama.chat(
            model="llama3",
            messages=[
                {
                "role": "user",
                "content": "Summarise concisely and succinctly the customer's context and what they want from me in bullet points.\n"
                        "Interprete and summarise recommended based on their context SPECIFIC securities like bonds, funds etc. in bullet points, including possible average yield.\n"
                        "If risk high, recommend securities with higher yields. if risk low, recommend lower yields for safety. Be specific including fund names.\n"
                        "Use hyphens to separate each point.\n"
                        "No asterisks, no emojis, no special characters.\n"
                        "No introduction like here is or conclusion.\n"
                        "Respond politely, friendly and professionally to the customer.\n"
                        "Only include practical steps — no emotional or psychological comments.\n"
                        "This is a financial advisory bot, so focus on practical financial advice."
                        "Don't mention any disclaimer. Use is aware of due diligence.\n"
                        f"Customer's Message: {text}"
                },
            ],
        )
        ollama_response = response["message"]["content"]
        print(ollama_response)

        send_message(ollama_response)




   