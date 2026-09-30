import os
import requests
from fastapi import FastAPI, Request

app = FastAPI()

BOT_TOKEN = os.environ.get("BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

@app.get("/")
def home():
    return {"status": "FinPulse Bot is Live and Connected!"}

@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    # यहाँ टेलीग्राम से आने वाले मैसेज को हैंडल किया जाएगा
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        
        # अगर यूजर /start लिखे तो बोट रिप्लाई करेगा
        if text == "/start":
            send_message(chat_id, "नमस्ते! FinPulse Bot एक्टिव है। यह आपके चैनल पर कॉर्पोरेट घोषणाओं के अलर्ट भेजेगा।")
            
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
