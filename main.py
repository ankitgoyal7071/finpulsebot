import os
import requests
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

app = FastAPI()

BOT_TOKEN = os.environ.get("BOT_TOKEN")
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# ऑटोमेटिक वेबहुक सेट करना
@app.on_event("startup")
def set_webhook():
    if BOT_TOKEN and RENDER_EXTERNAL_URL:
        webhook_url = f"{RENDER_EXTERNAL_URL}/webhook"
        url = f"{TELEGRAM_API_URL}/setWebhook?url={webhook_url}"
        try:
            requests.get(url)
        except Exception as e:
            print(f"Error setting webhook: {e}")

# यह रूट आपके मिनी ऐप का सुंदर यूजर इंटरफेस (UI) दिखाएगा
@app.get("/", response_class=HTMLResponse)
def mini_app_home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>FinPulse Mini App</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
    </head>
    <body class="bg-[#0f172a] text-white font-sans flex flex-col h-screen justify-between select-none">
        <!-- Header -->
        <div class="p-4 bg-[#1e293b] flex justify-between items-center border-b border-slate-800">
            <div class="flex items-center space-x-2">
                <span class="w-2.5 h-2.5 bg-emerald-500 rounded-full"></span>
                <h1 class="text-base font-bold tracking-wide">FinPulse</h1>
            </div>
            <span class="text-xs bg-slate-700 px-2.5 py-1 rounded-md text-slate-300 font-medium">USER</span>
        </div>

        <!-- Dynamic Content Area -->
        <div id="content" class="flex-1 p-4 overflow-y-auto">
            <div class="text-center py-16">
                <div class="text-4xl mb-3">📊</div>
                <h2 class="text-lg font-semibold mb-1">My Watchlist</h2>
                <p class="text-gray-400 text-xs px-6">Tracking 0 instruments. Search and follow NSE/BSE securities to receive alerts.</p>
            </div>
        </div>

        <!-- Bottom Navigation Bar -->
        <div class="flex justify-around bg-[#1e293b] py-3 border-t border-slate-800 text-xs">
            <button onclick="switchTab('watchlist', this)" class="nav-btn text-blue-400 font-semibold flex flex-col items-center">⭐ Watchlist</button>
            <button onclick="switchTab('results', this)" class="nav-btn text-gray-400 flex flex-col items-center">📅 Results</button>
            <button onclick="switchTab('search', this)" class="nav-btn text-gray-400 flex flex-col items-center">🔍 Search</button>
            <button onclick="switchTab('settings', this)" class="nav-btn text-gray-400 flex flex-col items-center">⚙️ Settings</button>
        </div>

        <script>
            const tg = window.Telegram.WebApp;
            tg.expand();

            function switchTab(tab, element) {
                // Active class handle
                document.querySelectorAll('.nav-btn').forEach(btn => {
                    btn.classList.remove('text-blue-400', 'font-semibold');
                    btn.classList.add('text-gray-400');
                });
                element.classList.remove('text-gray-400');
                element.classList.add('text-blue-400', 'font-semibold');

                const content = document.getElementById('content');
                if(tab === 'watchlist') {
                    content.innerHTML = `<div class="text-center py-16"><div class="text-4xl mb-3">📊</div><h2 class="text-lg font-semibold mb-1">My Watchlist</h2><p class="text-gray-400 text-xs px-6">Tracking 0 instruments. Search and follow NSE/BSE securities to receive alerts.</p></div>`;
                } else if(tab === 'results') {
                    content.innerHTML = `<div class="p-2"><h2 class="text-base font-semibold mb-1">Results Calendar</h2><p class="text-gray-400 text-xs mb-4">Companies announcing earnings</p><div class="bg-slate-800 p-3 rounded-lg border border-slate-700 text-xs text-gray-300">आज कोई बड़ा रिजल्ट शेड्यूल्ड नहीं है।</div></div>`;
                } else if(tab === 'search') {
                    content.innerHTML = `<div class="p-2"><h2 class="text-base font-semibold mb-2">Find Instruments</h2><input type="text" placeholder="Search Reliance, TATACAP, 500325..." class="w-full p-2.5 bg-slate-800 rounded-lg border border-slate-700 text-white text-xs outline-none focus:border-blue-500"></div>`;
                } else if(tab === 'settings') {
                    content.innerHTML = `<div class="p-2"><h2 class="text-base font-semibold mb-1">Settings</h2><p class="text-gray-400 text-xs mb-4">Account info & notification preferences</p><div class="bg-slate-800 p-3 rounded-lg border border-slate-700 text-xs space-y-2"><div class="flex justify-between"><span>Telegram ID:</span> <span class="text-blue-400">Connected</span></div><div class="flex justify-between"><span>Corporate Alerts:</span> <span class="text-emerald-400">Active</span></div></div></div>`;
                }
            }
        </script>
    </body>
    </html>
    """

@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        
        if text == "/start":
            send_webapp_button(chat_id)
            
    return {"ok": True}

def send_webapp_button(chat_id):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": "🚀 **FinPulse Mini App तैयार है!**\n\nनीचे दिए गए बटन पर क्लिक करके आप बिल्कुल प्रोफेशनल ट्रेडिंग ऐप जैसा इंटरफेस खोल सकते हैं:",
        "parse_mode": "Markdown",
        "reply_markup": {
            "inline_keyboard": [
                [
                    {
                        "text": "⚡ Open FinPulse Mini App",
                        "web_app": {"url": RENDER_EXTERNAL_URL}
                    }
                ]
            ]
        }
    }
    requests.post(url, json=payload)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
