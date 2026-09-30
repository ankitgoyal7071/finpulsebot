import os
import requests
from fastapi import FastAPI, Request

app = FastAPI()

BOT_TOKEN = os.environ.get("BOT_TOKEN")
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL")

TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# बोट स्टार्ट होते ही अपने आप वेबहुक सेट कर लेगा
@app.on_event("startup")
def set_webhook():
    if BOT_TOKEN and RENDER_EXTERNAL_URL:
        webhook_url = f"{RENDER_EXTERNAL_URL}/webhook"
        url = f"{TELEGRAM_API_URL}/setWebhook?url={webhook_url}"
        try:
            requests.get(url)
            print(f"Webhook automatically configured to: {webhook_url}")
        except Exception as e:
            print(f"Error setting webhook: {e}")

@app.get("/")
def home():
    return {"status": "FinPulse Bot is Live and Fully Connected!"}

@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        
        # जब आप /start लिखेंगे तो बोट यह जवाब देगा
        if text == "/start":
            send_message(chat_id, "🚀 **FinPulse Bot एक्टिव है!**\n\nआपका बोट सर्वर से सफलतापूर्वक जुड़ चुका है। अब हम इसमें एनएसई/बीएसई कॉर्पोरेट घोषणाओं (Corporate Actions) का लाइव डेटा जोड़ेंगे।")
            
    return {"ok": True}

def send_message(chat_id, text):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
