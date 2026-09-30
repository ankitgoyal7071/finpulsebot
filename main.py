import os
import requests
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

app = FastAPI()

BOT_TOKEN = os.environ.get("BOT_TOKEN")
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

@app.on_event("startup")
def set_webhook():
    if BOT_TOKEN and RENDER_EXTERNAL_URL:
        webhook_url = f"{RENDER_EXTERNAL_URL}/webhook"
        url = f"{TELEGRAM_API_URL}/setWebhook?url={webhook_url}"
        try:
            requests.get(url)
        except Exception as e:
            print(f"Error setting webhook: {e}")

@app.get("/", response_class=HTMLResponse)
def mini_app_home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>FinPulse</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
    </head>
    <body class="bg-[#0f172a] text-white font-sans flex flex-col h-screen justify-between select-none">
        
        <!-- Top Status Bar -->
        <div class="bg-[#1e293b] px-4 py-3 flex justify-between items-center border-b border-slate-800 text-xs">
            <div class="flex items-center space-x-2">
                <span class="w-2 h-2 bg-emerald-500 rounded-full"></span>
                <span class="font-semibold tracking-wide">Corporate Alerts</span>
            </div>
            <div class="flex items-center space-x-2">
                <span class="bg-slate-800 text-slate-300 px-2.5 py-1 rounded-md font-mono" id="top-username">@Optraderr</span>
                <span class="bg-slate-800 text-slate-300 px-2 py-1 rounded-md text-[10px] font-bold">USER</span>
            </div>
        </div>

        <!-- Dynamic Content Area -->
        <div id="content" class="flex-1 p-4 overflow-y-auto space-y-3">
            <!-- Default Watchlist Tab Content -->
            <div id="tab-watchlist" class="space-y-4">
                <div class="flex justify-between items-center">
                    <h2 class="text-base font-bold">My Watchlist</h2>
                    <button onclick="switchTab('search')" class="bg-blue-600 hover:bg-blue-500 text-white px-3 py-1.5 rounded-lg text-xs font-semibold">+ Add Stock</button>
                </div>
                <div id="watchlist-items" class="space-y-2">
                    <div class="text-center py-16 bg-[#1e293b]/50 rounded-xl border border-slate-800 p-4">
                        <div class="text-3xl mb-2">📊</div>
                        <h3 class="text-sm font-semibold mb-1">Your watchlist is empty</h3>
                        <p class="text-gray-400 text-[11px] mb-4">Search and follow NSE/BSE securities to receive alerts.</p>
                        <button onclick="switchTab('search')" class="bg-blue-600 text-white px-4 py-2 rounded-lg text-xs font-semibold">Find Instruments</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Bottom Navigation Bar -->
        <div class="flex justify-around bg-[#1e293b] py-2.5 border-t border-slate-800 text-[11px]">
            <button onclick="switchTab('watchlist', this)" class="nav-btn text-blue-400 font-semibold flex flex-col items-center">⭐ Watchlist</button>
            <button onclick="switchTab('results', this)" class="nav-btn text-gray-400 flex flex-col items-center">📅 Results</button>
            <button onclick="switchTab('search', this)" class="nav-btn text-gray-400 flex flex-col items-center">🔍 Search</button>
            <button onclick="switchTab('settings', this)" class="nav-btn text-gray-400 flex flex-col items-center">⚙️ Settings</button>
        </div>

        <script>
            const tg = window.Telegram.WebApp;
            tg.expand();

            // Fetch Telegram User Info
            const user = tg.initDataUnsafe && tg.initDataUnsafe.user ? tg.initDataUnsafe.user : { id: "1612210913", username: "Optraderr" };
            const userId = user.id || "1612210913";
            const username = user.username ? "@" + user.username : "@Optraderr";

            document.getElementById('top-username').innerText = username;

            let watchlist = [];

            function switchTab(tab, element) {
                if(element) {
                    document.querySelectorAll('.nav-btn').forEach(btn => {
                        btn.classList.remove('text-blue-400', 'font-semibold');
                        btn.classList.add('text-gray-400');
                    });
                    element.classList.remove('text-gray-400');
                    element.classList.add('text-blue-400', 'font-semibold');
                }

                const content = document.getElementById('content');
                
                if(tab === 'watchlist') {
                    if(watchlist.length === 0) {
                        content.innerHTML = `
                            <div class="space-y-4">
                                <div class="flex justify-between items-center"><h2 class="text-base font-bold">My Watchlist</h2><button onclick="switchTab('search')" class="bg-blue-600 text-white px-3 py-1.5 rounded-lg text-xs font-semibold">+ Add Stock</button></div>
                                <div class="text-center py-16 bg-[#1e293b]/50 rounded-xl border border-slate-800 p-4">
                                    <div class="text-3xl mb-2">📊</div>
                                    <h3 class="text-sm font-semibold mb-1">Your watchlist is empty</h3>
                                    <p class="text-gray-400 text-[11px] mb-4">Search and follow NSE/BSE securities to receive alerts.</p>
                                    <button onclick="switchTab('search')" class="bg-blue-600 text-white px-4 py-2 rounded-lg text-xs font-semibold">Find Instruments</button>
                                </div>
                            </div>`;
                    } else {
                        let html = `<div class="space-y-3"><div class="flex justify-between items-center"><h2 class="text-base font-bold">My Watchlist</h2><span class="text-xs text-gray-400">Tracking ${watchlist.length} instruments</span></div>`;
                        watchlist.forEach(item => {
                            html += `<div class="bg-[#1e293b] p-3 rounded-xl border border-slate-800 flex justify-between items-center"><div><h3 class="font-semibold text-xs">${item.name}</h3><p class="text-[10px] text-gray-400">${item.exchange}: ${item.code}</p></div><button onclick="removeFromWatchlist('${item.code}')" class="text-red-400 text-xs px-2.5 py-1 bg-red-950/40 rounded-lg">Unfollow</button></div>`;
                        });
                        html += `</div>`;
                        content.innerHTML = html;
                    }
                } 
                else if(tab === 'results') {
                    content.innerHTML = `
                        <div class="space-y-3">
                            <div><h2 class="text-base font-bold">Results Calendar</h2><p class="text-gray-400 text-xs">Companies announcing earnings</p></div>
                            <div class="flex space-x-1.5 overflow-x-auto pb-1 text-xs">
                                <button onclick="filterResults('all', this)" class="res-filter bg-blue-600 text-white px-3 py-1.5 rounded-lg whitespace-nowrap font-medium">All Upcoming</button>
                                <button onclick="filterResults('today', this)" class="res-filter bg-slate-800 text-gray-300 px-3 py-1.5 rounded-lg whitespace-nowrap font-medium">Today</button>
                                <button onclick="filterResults('tomorrow', this)" class="res-filter bg-slate-800 text-gray-300 px-3 py-1.5 rounded-lg whitespace-nowrap font-medium">Tomorrow</button>
                            </div>
                            <input type="text" placeholder="Search by company name or ticker..." oninput="searchCalendar(this.value)" class="w-full p-2.5 bg-[#1e293b] rounded-lg border border-slate-800 text-white text-xs outline-none focus:border-blue-500">
                            
                            <div id="results-list" class="space-y-2.5">
                                <div class="bg-[#1e293b] p-3 rounded-xl border border-slate-800 flex justify-between items-center">
                                    <div>
                                        <div class="flex items-center space-x-2 mb-1"><span class="font-semibold text-xs">BF Utilities Ltd</span><span class="bg-blue-950 text-blue-400 text-[9px] px-1.5 py-0.5 rounded font-mono">NSE</span></div>
                                        <p class="text-[10px] text-gray-400">📅 Wed, 30 Sept &nbsp;|&nbsp; Q1 FY26-27</p>
                                        <p class="text-[10px] text-gray-500 font-mono mt-0.5">NSE: BFUTILITIE | BSE: 532430</p>
                                    </div>
                                    <button onclick="toggleWatch('BF Utilities Ltd', 'NSE', '532430', this)" class="bg-blue-600 hover:bg-blue-500 text-white px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap">+ Watch</button>
                                </div>
                                <div class="bg-[#1e293b] p-3 rounded-xl border border-slate-800 flex justify-between items-center">
                                    <div>
                                        <div class="flex items-center space-x-2 mb-1"><span class="font-semibold text-xs">Globe Commercials Ltd</span><span class="bg-amber-950 text-amber-400 text-[9px] px-1.5 py-0.5 rounded font-mono">BSE</span></div>
                                        <p class="text-[10px] text-gray-400">📅 Wed, 30 Sept &nbsp;|&nbsp; Q1 FY26-27</p>
                                        <p class="text-[10px] text-gray-500 font-mono mt-0.5">BSE: 540266</p>
                                    </div>
                                    <button onclick="toggleWatch('Globe Commercials Ltd', 'BSE', '540266', this)" class="bg-blue-600 hover:bg-blue-500 text-white px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap">+ Watch</button>
                                </div>
                                <div class="bg-[#1e293b] p-3 rounded-xl border border-slate-800 flex justify-between items-center">
                                    <div>
                                        <div class="flex items-center space-x-2 mb-1"><span class="font-semibold text-xs">Manipal Payment & Identity Solutions</span><span class="bg-blue-950 text-blue-400 text-[9px] px-1.5 py-0.5 rounded font-mono">NSE</span></div>
                                        <p class="text-[10px] text-gray-400">📅 Thu, 1 Oct &nbsp;|&nbsp; Q2 FY26-27</p>
                                        <p class="text-[10px] text-gray-500 font-mono mt-0.5">NSE: MPIMANIPAL | BSE: 544916</p>
                                    </div>
                                    <button onclick="toggleWatch('Manipal Payment', 'NSE', '544916', this)" class="bg-blue-600 hover:bg-blue-500 text-white px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap">+ Watch</button>
                                </div>
                            </div>
                        </div>`;
                } 
                else if(tab === 'search') {
                    content.innerHTML = `
                        <div class="space-y-3">
                            <div><h2 class="text-base font-bold">Find Instruments</h2><p class="text-gray-400 text-xs">Search NSE symbols, BSE codes, ISIN, or company name</p></div>
                            <input type="text" id="searchInput" placeholder="Search e.g. Reliance, TATACAP, 500325..." oninput="performSearch(this.value)" class="w-full p-2.5 bg-[#1e293b] rounded-lg border border-slate-800 text-white text-xs outline-none focus:border-blue-500">
                            <div id="search-results" class="space-y-2">
                                <div class="bg-[#1e293b] p-3 rounded-xl border border-slate-800 flex justify-between items-center">
                                    <div><h3 class="font-semibold text-xs">Tata Consultancy Services Ltd</h3><p class="text-[10px] text-gray-400 font-mono mt-0.5">TCS &bull; 532540 &bull; INE467B01029</p></div>
                                    <button onclick="toggleWatch('Tata Consultancy Services', 'NSE', '532540', this)" class="bg-blue-600 text-white px-3 py-1.5 rounded-lg text-xs font-semibold">+ Follow</button>
                                </div>
                                <div class="bg-[#1e293b] p-3 rounded-xl border border-slate-800 flex justify-between items-center">
                                    <div><h3 class="font-semibold text-xs">Reliance Industries Ltd</h3><p class="text-[10px] text-gray-400 font-mono mt-0.5">RELIANCE &bull; 500325 &bull; INE002A01018</p></div>
                                    <button onclick="toggleWatch('Reliance Industries', 'NSE', '500325', this)" class="bg-blue-600 text-white px-3 py-1.5 rounded-lg text-xs font-semibold">+ Follow</button>
                                </div>
                            </div>
                        </div>`;
                } 
                else if(tab === 'settings') {
                    content.innerHTML = `
                        <div class="space-y-4">
                            <div><h2 class="text-base font-bold">Settings</h2><p class="text-gray-400 text-xs">Account info & notification preferences</p></div>
                            
                            <div class="bg-[#1e293b] p-3.5 rounded-xl border border-slate-800 space-y-2.5 text-xs">
                                <div class="text-[11px] font-bold text-gray-400 tracking-wider uppercase mb-1">Account Information</div>
                                <div class="flex justify-between py-1 border-b border-slate-800/60"><span class="text-gray-400">Telegram ID:</span> <span class="font-mono text-blue-400 font-semibold">${userId}</span></div>
                                <div class="flex justify-between py-1 border-b border-slate-800/60"><span class="text-gray-400">Username:</span> <span class="font-mono text-blue-400">${username}</span></div>
                                <div class="flex justify-between py-1 border-b border-slate-800/60"><span class="text-gray-400">Access Status:</span> <span class="text-emerald-400 font-bold">ACTIVE</span></div>
                                <div class="flex justify-between py-1"><span class="text-gray-400">Role:</span> <span class="bg-slate-800 px-2 py-0.5 rounded text-[10px] font-bold">USER</span></div>
                            </div>

                            <div class="bg-[#1e293b] p-3.5 rounded-xl border border-slate-800 space-y-3 text-xs">
                                <div class="text-[11px] font-bold text-gray-400 tracking-wider uppercase">Alert Preferences</div>
                                <div class="flex justify-between items-center">
                                    <div><div class="font-semibold">All announcements</div><div class="text-[10px] text-gray-400">Receive every new NSE/BSE corporate announcement.</div></div>
                                    <input type="checkbox" checked class="w-4 h-4 accent-blue-600 rounded cursor-pointer">
                                </div>
                                <div class="flex justify-between items-center pt-2 border-t border-slate-800/60">
                                    <div><div class="font-semibold">Auto-add upcoming results</div><div class="text-[10px] text-gray-400">Automatically add companies announcing results.</div></div>
                                    <input type="checkbox" checked class="w-4 h-4 accent-blue-600 rounded cursor-pointer">
                                </div>
                            </div>
                        </div>`;
                }
            }

            function toggleWatch(name, exchange, code, btn) {
                const exists = watchlist.find(i => i.code === code);
                if(!exists) {
                    watchlist.push({ name, exchange, code });
                    btn.innerText = "✓ Following";
                    btn.classList.remove('bg-blue-600', 'hover:bg-blue-500');
                    btn.classList.add('bg-emerald-600');
                } else {
                    watchlist = watchlist.filter(i => i.code !== code);
                    btn.innerText = "+ Watch";
                    btn.classList.remove('bg-emerald-600');
                    btn.classList.add('bg-blue-600', 'hover:bg-blue-500');
                }
            }

            function removeFromWatchlist(code) {
                watchlist = watchlist.filter(i => i.code !== code);
                switchTab('watchlist');
            }

            function filterResults(type, btn) {
                document.querySelectorAll('.res-filter').forEach(b => {
                    b.classList.remove('bg-blue-600', 'text-white');
                    b.classList.add('bg-slate-800', 'text-gray-300');
                });
                btn.classList.remove('bg-slate-800', 'text-gray-300');
                btn.classList.add('bg-blue-600', 'text-white');
            }

            function searchCalendar(query) {
                // Ticker search logic placeholder
            }

            function performSearch(query) {
                // Dynamic search placeholder
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
        "text": "⚡ **FinPulse Mini App तैयार है!**\n\nनीचे दिए गए बटन पर क्लिक करके अपना प्रोफेशनल ट्रेडिंग डैशबोर्ड खोलें:",
        "parse_mode": "Markdown",
        "reply_markup": {
            "inline_keyboard": [
                [
                    {
                        "text": "🚀 Open FinPulse Dashboard",
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
