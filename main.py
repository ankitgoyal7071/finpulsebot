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
        <title>FinPulse Pro</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
    </head>
    <body class="bg-[#0f172a] text-white font-sans flex flex-col h-screen justify-between select-none">
        
        <!-- Top Status Bar -->
        <div class="bg-[#1e293b] px-4 py-3 flex justify-between items-center border-b border-slate-800 text-xs">
            <div class="flex items-center space-x-2">
                <span class="w-2.5 h-2.5 bg-emerald-500 rounded-full animate-pulse"></span>
                <span class="font-bold tracking-wide">Corporate Alerts</span>
            </div>
            <div class="flex items-center space-x-2">
                <span class="bg-slate-800 text-slate-300 px-2.5 py-1 rounded-md font-mono" id="top-username">@Optraderr</span>
                <span class="bg-blue-600 text-white px-2 py-0.5 rounded text-[10px] font-bold">USER</span>
            </div>
        </div>

        <!-- Dynamic Content Area -->
        <div id="content" class="flex-1 p-4 overflow-y-auto space-y-3">
            <!-- Rendered via JS -->
        </div>

        <!-- Bottom Navigation Bar -->
        <div class="flex justify-around bg-[#1e293b] py-2.5 border-t border-slate-800 text-[11px]">
            <button onclick="switchTab('watchlist', this)" id="btn-watchlist" class="nav-btn text-blue-400 font-semibold flex flex-col items-center">⭐ Watchlist</button>
            <button onclick="switchTab('results', this)" id="btn-results" class="nav-btn text-gray-400 flex flex-col items-center">📅 Results</button>
            <button onclick="switchTab('search', this)" id="btn-search" class="nav-btn text-gray-400 flex flex-col items-center">🔍 Search</button>
            <button onclick="switchTab('settings', this)" id="btn-settings" class="nav-btn text-gray-400 flex flex-col items-center">⚙️ Settings</button>
        </div>

        <script>
            const tg = window.Telegram.WebApp;
            tg.expand();

            const user = tg.initDataUnsafe && tg.initDataUnsafe.user ? tg.initDataUnsafe.user : { id: "1612210913", username: "Optraderr" };
            const userId = user.id || "1612210913";
            const username = user.username ? "@" + user.username : "@Optraderr";
            document.getElementById('top-username').innerText = username;

            let watchlist = JSON.parse(localStorage.getItem('finpulse_watchlist')) || [];
            let settingsState = JSON.parse(localStorage.getItem('finpulse_settings')) || { allAnnouncements: true, autoAdd: true };
            
            let currentTab = 'watchlist';
            let currentFilter = 'all';

            // Real Listed Companies Results Calendar
            const allResults = [
                { name: "BF Utilities Ltd", exchange: "NSE", code: "BFUTILITIE", bse: "532430", date: "Wed, 30 Sept", type: "today", period: "Q1 FY26-27" },
                { name: "Globe Commercials Ltd", exchange: "BSE", code: "GLOBE", bse: "540266", date: "Wed, 30 Sept", type: "today", period: "Q1 FY26-27" },
                { name: "Manipal Payment & Identity Solutions", exchange: "NSE", code: "MPIMANIPAL", bse: "544916", date: "Thu, 1 Oct", type: "tomorrow", period: "Q2 FY26-27" },
                { name: "Pranav Constructions Ltd", exchange: "NSE", code: "PRANAV", bse: "544909", date: "Thu, 1 Oct", type: "tomorrow", period: "Q2 FY26-27" },
                { name: "Tata Consultancy Services Ltd", exchange: "NSE", code: "TCS", bse: "532540", date: "Fri, 2 Oct", type: "upcoming", period: "Q2 FY26-27" },
                { name: "Reliance Industries Ltd", exchange: "NSE", code: "RELIANCE", bse: "500325", date: "Sat, 3 Oct", type: "upcoming", period: "Q2 FY26-27" },
                { name: "Infosys Limited", exchange: "NSE", code: "INFY", bse: "500209", date: "Mon, 5 Oct", type: "upcoming", period: "Q2 FY26-27" },
                { name: "HDFC Bank Limited", exchange: "NSE", code: "HDFCBANK", bse: "500180", date: "Tue, 6 Oct", type: "upcoming", period: "Q2 FY26-27" },
                { name: "State Bank of India", exchange: "NSE", code: "SBIN", bse: "500112", date: "Wed, 7 Oct", type: "upcoming", period: "Q2 FY26-27" },
                { name: "ITC Limited", exchange: "NSE", code: "ITC", bse: "500875", date: "Thu, 8 Oct", type: "upcoming", period: "Q2 FY26-27" }
            ];

            // Official Listed Instruments Database (NSE/BSE)
            const allInstruments = [
                { name: "Tata Consultancy Services Ltd", symbol: "TCS", bse: "532540", isin: "INE467B01029" },
                { name: "Reliance Industries Ltd", symbol: "RELIANCE", bse: "500325", isin: "INE002A01018" },
                { name: "HDFC Bank Limited", symbol: "HDFCBANK", bse: "500180", isin: "INE040A01034" },
                { name: "Infosys Limited", symbol: "INFY", bse: "500209", isin: "INE009A01021" },
                { name: "State Bank of India", symbol: "SBIN", bse: "500112", isin: "INE062A01020" },
                { name: "ITC Limited", symbol: "ITC", bse: "500875", isin: "INE154A01025" },
                { name: "Bharti Airtel Ltd", symbol: "BHARTIARTL", bse: "532454", isin: "INE397D01024" },
                { name: "Larsen & Toubro Ltd", symbol: "LT", bse: "500510", isin: "INE018A01030" },
                { name: "Axis Bank Limited", symbol: "AXISBANK", bse: "532215", isin: "INE238A01034" },
                { name: "Kotak Mahindra Bank Ltd", symbol: "KOTAKBANK", bse: "500247", isin: "INE237A01028" },
                { name: "BF Utilities Ltd", symbol: "BFUTILITIE", bse: "532430", isin: "INE888C01010" },
                { name: "Globe Commercials Ltd", symbol: "GLOBE", bse: "540266", isin: "INE999D01017" },
                { name: "Manipal Payment & Identity Solutions", symbol: "MPIMANIPAL", bse: "544916", isin: "INE111E01015" },
                { name: "Pranav Constructions Ltd", symbol: "PRANAV", bse: "544909", isin: "INE222F01013" },
                { name: "Wipro Limited", symbol: "WIPRO", bse: "507685", isin: "INE075A01022" },
                { name: "Asian Paints Limited", symbol: "ASIANPAINT", bse: "500820", isin: "INE021A01026" },
                { name: "HCL Technologies Ltd", symbol: "HCLTECH", bse: "532281", isin: "INE860A01027" },
                { name: "Maruti Suzuki India Ltd", symbol: "MARUTI", bse: "532500", isin: "INE585B01010" },
                { name: "Tata Motors Ltd", symbol: "TATAMOTORS", bse: "500570", isin: "INE155A01022" },
                { name: "Tata Steel Ltd", symbol: "TATASTEEL", bse: "500470", isin: "INE081A01020" }
            ];

            function switchTab(tab, element) {
                currentTab = tab;
                if(!element) {
                    element = document.getElementById('btn-' + tab);
                }
                document.querySelectorAll('.nav-btn').forEach(btn => {
                    btn.classList.remove('text-blue-400', 'font-semibold');
                    btn.classList.add('text-gray-400');
                });
                if(element) {
                    element.classList.remove('text-gray-400');
                    element.classList.add('text-blue-400', 'font-semibold');
                }
                renderContent();
            }

            function renderContent() {
                const content = document.getElementById('content');
                
                if(currentTab === 'watchlist') {
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
                            html += `<div class="bg-[#1e293b] p-3 rounded-xl border border-slate-800 flex justify-between items-center"><div><h3 class="font-semibold text-xs">${item.name}</h3><p class="text-[10px] text-gray-400 font-mono mt-0.5">${item.exchange} &bull; ${item.code}</p></div><button onclick="removeFromWatchlist('${item.code}')" class="text-red-400 text-xs px-2.5 py-1 bg-red-950/40 rounded-lg">Unfollow</button></div>`;
                        });
                        html += `</div>`;
                        content.innerHTML = html;
                    }
                } 
                else if(currentTab === 'results') {
                    renderResultsView();
                } 
                else if(currentTab === 'search') {
                    renderSearchView(allInstruments);
                } 
                else if(currentTab === 'settings') {
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
                                    <input type="checkbox" id="setting-all" ${settingsState.allAnnouncements ? 'checked' : ''} onchange="updateSetting('allAnnouncements', this.checked)" class="w-4 h-4 accent-blue-600 rounded cursor-pointer">
                                </div>
                                <div class="flex justify-between items-center pt-2 border-t border-slate-800/60">
                                    <div><div class="font-semibold">Auto-add upcoming results</div><div class="text-[10px] text-gray-400">Automatically add companies announcing results.</div></div>
                                    <input type="checkbox" id="setting-auto" ${settingsState.autoAdd ? 'checked' : ''} onchange="updateSetting('autoAdd', this.checked)" class="w-4 h-4 accent-blue-600 rounded cursor-pointer">
                                </div>
                            </div>
                        </div>`;
                }
            }

            function renderResultsView(filteredList = null, searchQ = "") {
                const list = filteredList || getFilteredResults();
                const content = document.getElementById('content');
                
                content.innerHTML = `
                    <div class="space-y-3">
                        <div><h2 class="text-base font-bold">Results Calendar</h2><p class="text-gray-400 text-xs">${list.length} companies announcing earnings</p></div>
                        <div class="flex space-x-1.5 overflow-x-auto pb-1 text-xs">
                            <button onclick="setFilter('all', this)" class="res-filter ${currentFilter==='all'?'bg-blue-600 text-white':'bg-slate-800 text-gray-300'} px-3 py-1.5 rounded-lg whitespace-nowrap font-medium">All Upcoming</button>
                            <button onclick="setFilter('next2', this)" class="res-filter ${currentFilter==='next2'?'bg-blue-600 text-white':'bg-slate-800 text-gray-300'} px-3 py-1.5 rounded-lg whitespace-nowrap font-medium">Next 2 Days</button>
                            <button onclick="setFilter('today', this)" class="res-filter ${currentFilter==='today'?'bg-blue-600 text-white':'bg-slate-800 text-gray-300'} px-3 py-1.5 rounded-lg whitespace-nowrap font-medium">Today</button>
                            <button onclick="setFilter('tomorrow', this)" class="res-filter ${currentFilter==='tomorrow'?'bg-blue-600 text-white':'bg-slate-800 text-gray-300'} px-3 py-1.5 rounded-lg whitespace-nowrap font-medium">Tomorrow</button>
                        </div>
                        <input type="text" id="calendarSearchInput" value="${searchQ}" placeholder="Search by company name or ticker..." oninput="searchCalendar(this.value)" class="w-full p-2.5 bg-[#1e293b] rounded-lg border border-slate-800 text-white text-xs outline-none focus:border-blue-500">
                        
                        <div id="results-list" class="space-y-2.5">
                            ${list.length === 0 ? '<div class="text-center py-10 text-gray-400 text-xs">कोई रिजल्ट नहीं मिला।</div>' : ''}
                            ${list.map(item => {
                                const isFollowed = watchlist.some(w => w.code === item.code);
                                return `
                                <div class="bg-[#1e293b] p-3 rounded-xl border border-slate-800 flex justify-between items-center">
                                    <div>
                                        <div class="flex items-center space-x-2 mb-1"><span class="font-semibold text-xs">${item.name}</span><span class="bg-blue-950 text-blue-400 text-[9px] px-1.5 py-0.5 rounded font-mono">${item.exchange}</span></div>
                                        <p class="text-[10px] text-gray-400">📅 ${item.date} &nbsp;\vert{}&nbsp; ${item.period}</p>
                                        <p class="text-[10px] text-gray-500 font-mono mt-0.5">${item.exchange}: ${item.code} \vert{} BSE:${item.bse}</p>
                                    </div>
                                    <button onclick="toggleWatch('${item.name}', '${item.exchange}', '${item.code}')" class="${isFollowed?'bg-emerald-600':'bg-blue-600 hover:bg-blue-500'} text-white px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap">${isFollowed ? '✓ Following' : '+ Watch'}</button>
                                </div>`;
                            }).join('')}
                        </div>
                    </div>`;
            }

            function renderSearchView(instruments) {
                const content = document.getElementById('content');
                content.innerHTML = `
                    <div class="space-y-3">
                        <div><h2 class="text-base font-bold">Find Instruments</h2><p class="text-gray-400 text-xs">Search NSE symbols, BSE codes, ISIN, or company name</p></div>
                        <input type="text" id="searchInput" placeholder="Search e.g. Reliance, TATACAP, 500325..." oninput="performSearch(this.value)" class="w-full p-2.5 bg-[#1e293b] rounded-lg border border-slate-800 text-white text-xs outline-none focus:border-blue-500">
                        <div id="search-results" class="space-y-2">
                            ${instruments.length === 0 ? '<div class="text-center py-10 text-gray-400 text-xs">No instruments found.</div>' : ''}
                            ${instruments.map(inst => {
                                const isFollowed = watchlist.some(w => w.code === inst.symbol);
                                return `
                                <div class="bg-[#1e293b] p-3 rounded-xl border border-slate-800 flex justify-between items-center">
                                    <div><h3 class="font-semibold text-xs">${inst.name}</h3><p class="text-[10px] text-gray-400 font-mono mt-0.5">${inst.symbol} &bull; ${inst.bse} &bull; ${inst.isin}</p></div>
                                    <button onclick="toggleWatch('${inst.name}', 'NSE', '${inst.symbol}')" class="${isFollowed?'bg-emerald-600':'bg-blue-600'} text-white px-3 py-1.5 rounded-lg text-xs font-semibold">${isFollowed ? '✓ Following' : '+ Follow'}</button>
                                </div>`;
                            }).join('')}
                        </div>
                    </div>`;
            }

            function getFilteredResults() {
                let filtered = allResults;
                if(currentFilter === 'today') {
                    filtered = allResults.filter(i => i.type === 'today');
                } else if(currentFilter === 'tomorrow') {
                    filtered = allResults.filter(i => i.type === 'tomorrow');
                } else if(currentFilter === 'next2') {
                    filtered = allResults.filter(i => i.type === 'today' || i.type === 'tomorrow');
                }
                return filtered;
            }

            function setFilter(type) {
                currentFilter = type;
                renderResultsView();
            }

            function searchCalendar(query) {
                const q = query.toLowerCase();
                let filtered = getFilteredResults();
                if(q) {
                    filtered = filtered.filter(i => i.name.toLowerCase().includes(q) || i.code.toLowerCase().includes(q) || i.bse.includes(q));
                }
                renderResultsView(filtered, query);
            }

            function performSearch(query) {
                const q = query.toLowerCase();
                let filtered = allInstruments.filter(i => i.name.toLowerCase().includes(q) || i.symbol.toLowerCase().includes(q) || i.bse.includes(q) || i.isin.toLowerCase().includes(q));
                
                renderSearchView(filtered);
                const inputEl = document.getElementById('searchInput');
                if(inputEl) {
                    inputEl.value = query;
                    inputEl.focus();
                }
            }

            function toggleWatch(name, exchange, code) {
                const exists = watchlist.find(i => i.code === code);
                if(!exists) {
                    watchlist.push({ name, exchange, code });
                } else {
                    watchlist = watchlist.filter(i => i.code !== code);
                }
                localStorage.setItem('finpulse_watchlist', JSON.stringify(watchlist));
                renderContent();
            }

            function removeFromWatchlist(code) {
                watchlist = watchlist.filter(i => i.code !== code);
                localStorage.setItem('finpulse_watchlist', JSON.stringify(watchlist));
                renderContent();
            }

            function updateSetting(key, value) {
                settingsState[key] = value;
                localStorage.setItem('finpulse_settings', JSON.stringify(settingsState));
            }

            renderContent();
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
        "text": "🚀 **FinPulse Pro मिनी ऐप अपडेट हो चुका है!**\n\nअब केवल असली NSE/BSE लिस्टेड कंपनियां ही सर्च में आएंगी। ओपन करने के लिए नीचे दिए गए बटन पर क्लिक करें:",
        "parse_mode": "Markdown",
        "reply_markup": {
            "inline_keyboard": [
                [
                    {
                        "text": "⚡ Open FinPulse Dashboard",
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
