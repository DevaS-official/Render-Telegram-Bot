import requests
import random
import os
from datetime import datetime
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

# 🔐 ENV
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID") 
HF_TOKEN = os.getenv("HF_TOKEN")

DATA_FILE = "data.txt"

# 📊 Daily limit check
def can_send_today():
    today = str(datetime.now().date())

    try:
        with open(DATA_FILE, "r") as f:
            saved_date, count = f.read().split(",")
            count = int(count)
    except:
        saved_date = ""
        count = 0

    if saved_date != today:
        count = 0

    if count < 5:
        return True, count, today
    return False, count, today

def update_count(today, count):
    with open(DATA_FILE, "w") as f:
        f.write(f"{today},{count}")

# 🤖 AI
def generate_ai_message():
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "meta-llama/llama-3-8b-instruct",
        "messages": [
            {
                "role": "system",
                "content": "Reply in ONE short Tanglish sentence like a casual Gen Z friend."
            },
            {
                "role": "user",
                "content": "Send one random casual Tanglish message."
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        msg = data["choices"][0]["message"]["content"]
        return msg.strip().split("\n")[0]
    except:
        return "dei konjam life ah serious ah eduthuko da 😴"

# 📩 Telegram
def send_message(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })

# 🎯 MAIN TRIGGER
@app.route('/ai-test')
def ai_test():
    allowed, count, today = can_send_today()

    # 🎲 probability (for 1-hour cron)
    if allowed and random.random() < 0.2:
        msg = generate_ai_message()
        send_message(msg)
        update_count(today, count + 1)
        return f"Sent {count+1}/5"

    return f"Skipped {count}/5"

# 🚀 RUN
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
