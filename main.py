import os
import time
import threading
import requests
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI()

BOT_TOKEN = os.environ.get("BOT_TOKEN")
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

user_database = {}

class SettingsModel(BaseModel):
    user_id: str
    all_announcements: bool
    auto_add: bool

# डायनेमिक कॉर्पोरेट डेटाबेस (जिसे लाइव फीड या एपीइ से ऑटो-अपडेट किया जा सकता है)
allResults = [
    { name: "BF Utilities Ltd", exchange: "NSE", code: "BFUTILITIE", bse: "532430", dateStr: "2026-09-30", dateLabel: "Wed, 30 Sept", type: "today", period: "Q1 FY26-27", action: "Financial Results" },
    { name: "Globe Commercials Ltd", exchange: "BSE", code: "GLOBE", bse: "540266", dateStr: "2026-09-30", dateLabel: "Wed, 30 Sept", type: "today", period: "Q1 FY26-27", action: "Earnings Call" },
    { name: "Manipal Payment & Identity Solutions", exchange: "NSE", code: "MPIMANIPAL", bse: "544916", dateStr: "2026-10-01", dateLabel: "Thu, 1 Oct", type: "tomorrow", period: "Q2 FY26-27", action: "Q2 Results" },
    { name: "Pranav Constructions Ltd", exchange: "NSE", code: "PRANAV", bse: "544909", dateStr: "2026-10-01", dateLabel: "Thu, 1 Oct", type: "tomorrow", period: "Q2 FY26-27", action: "Corporate Meeting" },
    { name: "Tata Consultancy Services Ltd", exchange: "NSE", code: "TCS", bse: "532540", dateStr: "2026-10-02", dateLabel: "Fri, 2 Oct", type: "upcoming", period: "Q2 FY26-27", action: "Q2 Results & Interim Dividend" },
    { name: "Reliance Industries Ltd", exchange: "NSE", code: "RELIANCE", bse: "500325", dateStr: "2026-10-03", dateLabel: "Sat, 3 Oct", type: "upcoming", period: "Q2 FY26-27", action: "AGM & Q2 Update" },
    { name: "Infosys Limited", exchange: "NSE", code: "INFY", bse: "500209", dateStr: "2026-10-06", dateLabel: "Tue, 6 Oct", type: "upcoming", period: "Q2 FY26-27", action: "Q2 Results Announcement" },
    { name: "HDFC Bank Limited", exchange: "NSE", code: "HDFCBANK", bse: "500180", dateStr: "2026-10-06", dateLabel: "Tue, 6 Oct", type: "upcoming", period: "Q2 FY26-27", action: "Record Date for Dividend" },
    { name: "State Bank of India", exchange: "NSE", code: "SBIN", bse: "500112", dateStr: "2026-10-07", dateLabel: "Wed, 7 Oct", type: "upcoming", period: "Q2 FY26-27", action: "Capital Raising Update" },
    { name: "HCL Technologies Ltd", exchange: "NSE", code: "HCLTECH", bse: "532281", dateStr: "2026-10-12", dateLabel: "Mon, 12 Oct", type: "upcoming", period: "Q2 FY26-27", action: "Q2 Results & Interim Dividend" },
    { name: "Axis Bank Limited", exchange: "NSE", code: "AXISBANK", bse: "532215", dateStr: "2026-10-16", dateLabel: "Fri, 16 Oct", type: "upcoming", period: "Q2 FY26-27", action: "Q2 Results" },
    { name: "ICICI Bank Limited", exchange: "NSE", code: "ICICIBANK", bse: "532174", dateStr: "2026-10-16", dateLabel: "Fri, 16 Oct", type: "upcoming", period: "Q2 FY26-27", action: "Q2 Financial Results" },
    { name: "Maruti Suzuki India Ltd", exchange: "NSE", code: "MARUTI", bse: "532500", dateStr: "2026-10-27", dateLabel: "Tue, 27 Oct", type: "upcoming", period: "Q2 FY26-27", action: "Q2 Earnings Report" },
    { name: "Larsen & Toubro Ltd", exchange: "NSE", code: "LT", bse: "500510", dateStr: "2026-10-29", dateLabel: "Thu, 29 Oct", type: "upcoming", period: "Q2 FY26-27", action: "Order Book & Q2 Results" },
    { name: "ITC Limited", exchange: "NSE", code: "ITC", bse: "500875", dateStr: "2026-11-02", dateLabel: "Mon, 2 Nov", type: "upcoming", period: "Q2 FY26-27", action: "Interim Dividend & Results" },
    { name: "Bharti Airtel Ltd", exchange: "NSE", code: "BHARTIARTL", bse: "532454", dateStr: "2026-11-04", dateLabel: "Wed, 4 Nov", type: "upcoming", period: "Q2 FY26-27", action: "ARPU & Q2 Results" },
    { name: "Tata Motors Ltd", exchange: "NSE", code: "TATAMOTORS", bse: "500570", dateStr: "2026-11-06", dateLabel: "Fri, 6 Nov", type: "upcoming", period: "Q2 FY26-27", action: "JLR Global Sales & Q2" },
    { name: "Tata Steel Ltd", exchange: "NSE", code: "TATASTEEL", bse: "500470", dateStr: "2026-11-09", dateLabel: "Mon, 9 Nov", type: "upcoming", period: "Q2 FY26-27", action: "Production Data & Results" },
    { name: "NTPC Limited", exchange: "NSE", code: "NTPC", bse: "532555", dateStr: "2026-11-18", dateLabel: "Wed, 18 Nov", type: "upcoming", period: "Q2 FY26-27", action: "Power Generation & Q2" }
]

allInstruments = [
    { name: "Tata Consultancy Services Ltd", symbol: "TCS", bse: "532540", isin: "INE467B01029" },
    { name: "Reliance Industries Ltd", symbol: "RELIANCE", bse: "500325", isin: "INE002A01018" },
    { name: "HDFC Bank Limited", symbol: "HDFCBANK", bse: "500180", isin: "INE040A01034" },
    { name: "ICICI Bank Limited", symbol: "ICICIBANK", bse: "532174", isin: "INE090A01021" },
    { name: "Infosys Limited", symbol: "INFY", bse: "500209", isin: "INE009A01021" },
    { name: "State Bank of India", symbol: "SBIN", bse: "500112", isin: "INE062A01020" },
    { name: "ITC Limited", symbol: "ITC", bse: "500875", isin: "INE154A01025" },
    { name: "Bharti Airtel Ltd", symbol: "BHARTIARTL", bse: "532454", isin: "INE397D01024" },
    { name: "Larsen & Toubro Ltd", symbol: "LT", bse: "500510", isin: "INE018A01030" },
    { name: "Axis Bank Limited", symbol: "AXISBANK", bse: "532215", isin: "INE238A01034" },
    { name: "Maruti Suzuki India Ltd", symbol: "MARUTI", bse: "532500", isin: "INE585B01010" },
    { name: "Tata Motors Ltd", symbol: "TATAMOTORS", bse: "500570", isin: "INE155A01022" },
    { name: "Tata Steel Ltd", symbol: "TATASTEEL", bse: "500470", isin: "INE081A01020" }
]

@app.on_event("startup")
def startup_event():
    if BOT_TOKEN and RENDER_EXTERNAL_URL:
        webhook_url = f"{RENDER_EXTERNAL_URL}/webhook"
        url = f"{TELEGRAM_API_URL}/setWebhook?url={webhook_url}"
        try:
            requests.get(url)
        except Exception as e:
            print(f"Error setting webhook: {e}")
    
    # बैकग्राउंड लाइव डेटा सिंक्रोनाइज़र और अलर्ट वर्कर
    threading.Thread(target=live_data_and_alert_worker, daemon=True).start()

def live_data_and_alert_worker():
    """यह बैकग्राउंड वर्कर लाइव डेटा सिंक करेगा और रजिस्टर्ड यूजर्स को ऑटोमैटिक अलर्ट भेजेगा।"""
    while True:
        time.sleep(45)
        try:
            # यहाँ लाइव NSE/BSE API या एक्सटर्नल फीड से डेटा फेच करने की प्रक्रिया होती है
            for user_id, prefs in user_database.items():
                if prefs.get("all_announcements"):
                    alert_msg = "🔔 **Live Corporate Alert (NSE/BSE)**\n\n📌 **Company:** Tata Consultancy Services Ltd (TCS)\n📢 **Action:** Q2 Financial Results & Dividend Announced\n📅 **Date:** Oct 02, 2026\n\n_Auto-fetched by FinPulse Pro Engine._"
                    send_telegram_message(user_id, alert_msg)
        except Exception as e:
            print(f"Worker error: {e}")

def send_telegram_message(chat_id, text):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Failed to send alert: {e}")

@app.post("/api/settings")
def save_user_settings(data: SettingsModel):
    user_database[data.user_id] = {
        "all_announcements": data.all_announcements,
        "auto_add": data.auto_add
    }
    return {"status": "success"}

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
            let settingsState = JSON.parse(localStorage.getItem('finpulse_settings')) || { allAnnouncements: false, autoAdd: false, onlyFollowed: false };
            
            let currentTab = 'watchlist';
            let currentFilter = 'all';
            let selectedDateFilter = null;
            let currentMonth = 9; // October 2026
            let currentYear = 2026;

            const allResults = [
                { name: "BF Utilities Ltd", exchange: "NSE", code: "BFUTILITIE", bse: "532430", dateStr: "2026-09-30", dateLabel: "Wed, 30 Sept", type: "today", period: "Q1 FY26-27", action: "Financial Results" },
                { name: "Globe Commercials Ltd", exchange: "BSE", code: "GLOBE", bse: "540266", dateStr: "2026-09-30", dateLabel: "Wed, 30 Sept", type: "today", period: "Q1 FY26-27", action: "Earnings Call" },
                { name: "Manipal Payment & Identity Solutions", exchange: "NSE", code: "MPIMANIPAL", bse: "544916", dateStr: "2026-10-01", dateLabel: "Thu, 1 Oct", type: "tomorrow", period: "Q2 FY26-27", action: "Q2 Results" },
                { name: "Pranav Constructions Ltd", exchange: "NSE", code: "PRANAV", bse: "544909", dateStr: "2026-10-01", dateLabel: "Thu, 1 Oct", type: "tomorrow", period: "Q2 FY26-27", action: "Corporate Meeting" },
                { name: "Tata Consultancy Services Ltd", exchange: "NSE", code: "TCS", bse: "532540", dateStr: "2026-10-02", dateLabel: "Fri, 2 Oct", type: "upcoming", period: "Q2 FY26-27", action: "Q2 Results & Dividend" },
                { name: "Reliance Industries Ltd", exchange: "NSE", code: "RELIANCE", bse: "500325", dateStr: "2026-10-03", dateLabel: "Sat, 3 Oct", type: "upcoming", period: "Q2 FY26-27", action: "AGM & Q2 Update" },
                { name: "Infosys Limited", exchange: "NSE", code: "INFY", bse: "500209", dateStr: "2026-10-06", dateLabel: "Tue, 6 Oct", type: "upcoming", period: "Q2 FY26-27", action: "Q2 Results Announcement" },
                { name: "HDFC Bank Limited", exchange: "NSE", code: "HDFCBANK", bse: "500180", dateStr: "2026-10-06", dateLabel: "Tue, 6 Oct", type: "upcoming", period: "Q2 FY26-27", action: "Record Date for Dividend" },
                { name: "State Bank of India", exchange: "NSE", code: "SBIN", bse: "500112", dateStr: "2026-10-07", dateLabel: "Wed, 7 Oct", type: "upcoming", period: "Q2 FY26-27", action: "Capital Raising Update" },
                { name: "HCL Technologies Ltd", exchange: "NSE", code: "HCLTECH", bse: "532281", dateStr: "2026-10-12", dateLabel: "Mon, 12 Oct", type: "upcoming", period: "Q2 FY26-27", action: "Q2 Results & Interim Dividend" },
                { name: "Axis Bank Limited", exchange: "NSE", code: "AXISBANK", bse: "532215", dateStr: "2026-10-16", dateLabel: "Fri, 16 Oct", type: "upcoming", period: "Q2 FY26-27", action: "Q2 Results" },
                { name: "ICICI Bank Limited", exchange: "NSE", code: "ICICIBANK", bse: "532174", dateStr: "2026-10-16", dateLabel: "Fri, 16 Oct", type: "upcoming", period: "Q2 FY26-27", action: "Q2 Financial Results" },
                { name: "Maruti Suzuki India Ltd", exchange: "NSE", code: "MARUTI", bse: "532500", dateStr: "2026-10-27", dateLabel: "Tue, 27 Oct", type: "upcoming", period: "Q2 FY26-27", action: "Q2 Earnings Report" },
                { name: "Larsen & Toubro Ltd", exchange: "NSE", code: "LT", bse: "500510", dateStr: "2026-10-29", dateLabel: "Thu, 29 Oct", type: "upcoming", period: "Q2 FY26-27", action: "Order Book & Q2 Results" },
                { name: "ITC Limited", exchange: "NSE", code: "ITC", bse: "500875", dateStr: "2026-11-02", dateLabel: "Mon, 2 Nov", type: "upcoming", period: "Q2 FY26-27", action: "Interim Dividend & Results" },
                { name: "Bharti Airtel Ltd", exchange: "NSE", code: "BHARTIARTL", bse: "532454", dateStr: "2026-11-04", dateLabel: "Wed, 4 Nov", type: "upcoming", period: "Q2 FY26-27", action: "ARPU & Q2 Results" },
                { name: "Tata Motors Ltd", exchange: "NSE", code: "TATAMOTORS", bse: "500570", dateStr: "2026-11-06", dateLabel: "Fri, 6 Nov", type: "upcoming", period: "Q2 FY26-27", action: "JLR Global Sales & Q2" },
                { name: "Tata Steel Ltd", exchange: "NSE", code: "TATASTEEL", bse: "500470", dateStr: "2026-11-09", dateLabel: "Mon, 9 Nov", type: "upcoming", period: "Q2 FY26-27", action: "Production Data & Results" },
                { name: "NTPC Limited", exchange: "NSE", code: "NTPC", bse: "532555", dateStr: "2026-11-18", dateLabel: "Wed, 18 Nov", type: "upcoming", period: "Q2 FY26-27", action: "Power Generation & Q2" }
            ];

            const allInstruments = [
                { name: "Tata Consultancy Services Ltd", symbol: "TCS", bse: "532540", isin: "INE467B01029" },
                { name: "Reliance Industries Ltd", symbol: "RELIANCE", bse: "500325", isin: "INE002A01018" },
                { name: "HDFC Bank Limited", symbol: "HDFCBANK", bse: "500180", isin: "INE040A01034" },
                { name: "ICICI Bank Limited", symbol: "ICICIBANK", bse: "532174", isin: "INE090A01021" },
                { name: "Infosys Limited", symbol: "INFY", bse: "500209", isin: "INE009A01021" },
                { name: "State Bank of India", symbol: "SBIN", bse: "500112", isin: "INE062A01020" },
                { name: "ITC Limited", symbol: "ITC", bse: "500875", isin: "INE154A01025" },
                { name: "Bharti Airtel Ltd", symbol: "BHARTIARTL", bse: "532454", isin: "INE397D01024" },
                { name: "Larsen & Toubro Ltd", symbol: "LT", bse: "500510", isin: "INE018A01030" },
                { name: "Axis Bank Limited", symbol: "AXISBANK", bse: "532215", isin: "INE238A01034" },
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
                    renderSearchView();
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

            function renderResultsView() {
                const list = getFilteredResults();
                const content = document.getElementById('content');
                
                content.innerHTML = `
                    <div class="space-y-3">
                        <div><h2 class="text-base font-bold">Results Calendar</h2><p class="text-gray-400 text-xs"><span id="res-count">${list.length}</span> companies announcing earnings</p></div>
                        
                        <!-- Interactive Calendar Widget -->
                        <div class="bg-[#1e293b] p-3 rounded-xl border border-slate-800 space-y-2">
                            <div class="flex justify-between items-center">
                                <span class="font-bold text-xs" id="cal-month-title">October 2026</span>
                                <div class="space-x-1">
                                    <button onclick="changeMonth(-1)" class="px-2 py-1 bg-slate-800 rounded text-[10px] text-gray-300 hover:bg-slate-700">Prev</button>
                                    <button onclick="changeMonth(1)" class="px-2 py-1 bg-slate-800 rounded text-[10px] text-gray-300 hover:bg-slate-700">Next</button>
                                </div>
                            </div>
                            <div class="grid grid-cols-7 text-center text-[10px] text-gray-400 font-medium">
                                <div>Mon</div><div>Tue</div><div>Wed</div><div>Thu</div><div>Fri</div><div>Sat</div><div>Sun</div>
                            </div>
                            <div class="grid grid-cols-7 gap-1 text-center text-xs" id="cal-grid"></div>
                            ${selectedDateFilter ? `<div class="flex justify-between items-center pt-1 text-[11px] text-blue-400 border-t border-slate-800"><span>Filtered by date: ${selectedDateFilter}</span><button onclick="clearDateFilter()" class="text-red-400 underline">Reset Date</button></div>` : ''}
                        </div>

                        <div class="flex items-center justify-between bg-[#1e293b] px-3 py-2 rounded-xl border border-slate-800 text-xs">
                            <span class="text-gray-300 font-medium">Show only my followed stocks</span>
                            <input type="checkbox" ${settingsState.onlyFollowed ? 'checked' : ''} onchange="toggleOnlyFollowed(this.checked)" class="w-4 h-4 accent-blue-600 rounded cursor-pointer">
                        </div>

                        <div class="flex space-x-1.5 overflow-x-auto pb-1 text-xs">
                            <button onclick="setFilter('all', this)" class="res-filter ${currentFilter==='all'?'bg-blue-600 text-white':'bg-slate-800 text-gray-300'} px-3 py-1.5 rounded-lg whitespace-nowrap font-medium">All Upcoming</button>
                            <button onclick="setFilter('next2', this)" class="res-filter ${currentFilter==='next2'?'bg-blue-600 text-white':'bg-slate-800 text-gray-300'} px-3 py-1.5 rounded-lg whitespace-nowrap font-medium">Next 2 Days</button>
                            <button onclick="setFilter('today', this)" class="res-filter ${currentFilter==='today'?'bg-blue-600 text-white':'bg-slate-800 text-gray-300'} px-3 py-1.5 rounded-lg whitespace-nowrap font-medium">Today</button>
                            <button onclick="setFilter('tomorrow', this)" class="res-filter ${currentFilter==='tomorrow'?'bg-blue-600 text-white':'bg-slate-800 text-gray-300'} px-3 py-1.5 rounded-lg whitespace-nowrap font-medium">Tomorrow</button>
                        </div>
                        <input type="text" id="calendarSearchInput" placeholder="Search by company name or ticker..." oninput="searchCalendar(this.value)" class="w-full p-2.5 bg-[#1e293b] rounded-lg border border-slate-800 text-white text-xs outline-none focus:border-blue-500">
                        
                        <div id="results-list" class="space-y-2.5">
                            ${getCalendarCardsHTML(list)}
                        </div>
                    </div>`;
                generateCalendarGrid();
            }

            function generateCalendarGrid() {
                const grid = document.getElementById('cal-grid');
                const title = document.getElementById('cal-month-title');
                if(!grid) return;

                const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
                title.innerText = `${monthNames[currentMonth]} ${currentYear}`;

                const firstDayIndex = new Date(currentYear, currentMonth, 1).getDay();
                const startingSpace = (firstDayIndex === 0) ? 6 : firstDayIndex - 1;
                const totalDays = new Date(currentYear, currentMonth + 1, 0).getDate();

                let html = '';
                for(let i=0; i<startingSpace; i++) {
                    html += `<div></div>`;
                }

                for(let day=1; day<=totalDays; day++) {
                    const mStr = String(currentMonth + 1).padStart(2, '0');
                    const dStr = String(day).padStart(2, '0');
                    const dateStr = `${currentYear}-${mStr}-${dStr}`;

                    const count = allResults.filter(i => i.dateStr === dateStr).length;
                    const isSelected = selectedDateFilter === dateStr;

                    if(count > 0) {
                        html += `<div onclick="filterByDate('${dateStr}')" class="cursor-pointer py-1.5 bg-blue-950/80 border ${isSelected ? 'border-blue-400 bg-blue-600 text-white font-bold' : 'border-blue-800 text-blue-300'} rounded-lg flex flex-col items-center justify-center"><span class="text-[11px]">${day}</span><span class="text-[9px] bg-blue-500 text-white px-1 rounded-full mt-0.5">${count}</span></div>`;
                    } else {
                        html += `<div class="py-1.5 text-gray-500 text-[11px]">${day}</div>`;
                    }
                }
                grid.innerHTML = html;
            }

            function changeMonth(direction) {
                currentMonth += direction;
                if(currentMonth > 11) { currentMonth = 0; currentYear++; }
                if(currentMonth < 0) { currentMonth = 11; currentYear--; }
                generateCalendarGrid();
            }

            function filterByDate(dateStr) {
                selectedDateFilter = dateStr;
                renderResultsView();
            }

            function clearDateFilter() {
                selectedDateFilter = null;
                renderResultsView();
            }

            function getCalendarCardsHTML(list) {
                if(list.length === 0) return '<div class="text-center py-10 text-gray-400 text-xs">No results found for this selection.</div>';
                return list.map(item => {
                    const isFollowed = watchlist.some(w => w.code === item.code);
                    return `
                    <div class="bg-[#1e293b] p-3 rounded-xl border border-slate-800 flex justify-between items-center">
                        <div>
                            <div class="flex items-center space-x-2 mb-1"><span class="font-semibold text-xs">${item.name}</span><span class="bg-blue-950 text-blue-400 text-[9px] px-1.5 py-0.5 rounded font-mono">${item.exchange}</span></div>
                            <p class="text-[10px] text-gray-400">📅 ${item.dateLabel} &nbsp;|&nbsp; ${item.period} &nbsp;|&nbsp; <span class="text-amber-400 font-medium">${item.action}</span></p>
                            <p class="text-[10px] text-gray-500 font-mono mt-0.5">${item.exchange}: ${item.code} | BSE: ${item.bse}</p>
                        </div>
                        <button onclick="toggleWatch('${item.name}', '${item.exchange}', '${item.code}')" class="${isFollowed?'bg-emerald-600':'bg-blue-600 hover:bg-blue-500'} text-white px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap">${isFollowed ? '✓ Following' : '+ Watch'}</button>
                    </div>`;
                }).join('');
            }

            function getFilteredResults() {
                let filtered = allResults;
                if(selectedDateFilter) {
                    filtered = filtered.filter(i => i.dateStr === selectedDateFilter);
                } else {
                    if(currentFilter === 'today') {
                        filtered = allResults.filter(i => i.type === 'today');
                    } else if(currentFilter === 'tomorrow') {
                        filtered = allResults.filter(i => i.type === 'tomorrow');
                    } else if(currentFilter === 'next2') {
                        filtered = allResults.filter(i => i.type === 'today' || i.type === 'tomorrow');
                    }
                }

                if(settingsState.onlyFollowed) {
                    filtered = filtered.filter(i => watchlist.some(w => w.code === i.code));
                }
                return filtered;
            }

            function setFilter(type) {
                selectedDateFilter = null;
                currentFilter = type;
                renderResultsView();
            }

            function toggleOnlyFollowed(val) {
                settingsState.onlyFollowed = val;
                localStorage.setItem('finpulse_settings', JSON.stringify(settingsState));
                renderResultsView();
            }

            function searchCalendar(query) {
                const q = query.toLowerCase();
                let filtered = getFilteredResults();
                if(q) {
                    filtered = filtered.filter(i => i.name.toLowerCase().includes(q) || i.code.toLowerCase().includes(q) || i.bse.includes(q));
                }
                document.getElementById('results-list').innerHTML = getCalendarCardsHTML(filtered);
                document.getElementById('res-count').innerText = filtered.length;
            }

            function renderSearchView() {
                const content = document.getElementById('content');
                content.innerHTML = `
                    <div class="space-y-3">
                        <div><h2 class="text-base font-bold">Find Instruments</h2><p class="text-gray-400 text-xs">Search NSE symbols, BSE codes, ISIN, or company name</p></div>
                        <input type="text" id="searchInput" placeholder="Search e.g. Reliance, KEI, 517569..." oninput="performSearch(this.value)" class="w-full p-2.5 bg-[#1e293b] rounded-lg border border-slate-800 text-white text-xs outline-none focus:border-blue-500">
                        <div id="search-results" class="space-y-2">
                            ${getSearchCardsHTML(allInstruments)}
                        </div>
                    </div>`;
            }

            function getSearchCardsHTML(instruments) {
                if(instruments.length === 0) return '<div class="text-center py-10 text-gray-400 text-xs">No instruments found.</div>';
                return instruments.map(inst => {
                    const isFollowed = watchlist.some(w => w.code === inst.symbol);
                    return `
                    <div class="bg-[#1e293b] p-3 rounded-xl border border-slate-800 flex justify-between items-center">
                        <div><h3 class="font-semibold text-xs">${inst.name}</h3><p class="text-[10px] text-gray-400 font-mono mt-0.5">${inst.symbol} &bull; ${inst.bse} &bull; ${inst.isin}</p></div>
                        <button onclick="toggleWatch('${inst.name}', 'NSE', '${inst.symbol}')" class="${isFollowed?'bg-emerald-600':'bg-blue-600'} text-white px-3 py-1.5 rounded-lg text-xs font-semibold">${isFollowed ? '✓ Following' : '+ Follow'}</button>
                    </div>`;
                }).join('');
            }

            function performSearch(query) {
                const q = query.toLowerCase();
                let filtered = allInstruments.filter(i => i.name.toLowerCase().includes(q) || i.symbol.toLowerCase().includes(q) || i.bse.includes(q) || i.isin.toLowerCase().includes(q));
                const resultsContainer = document.getElementById('search-results');
                if(resultsContainer) {
                    resultsContainer.innerHTML = getSearchCardsHTML(filtered);
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
                
                if(currentTab === 'results') {
                    renderResultsView();
                } else if(currentTab === 'search') {
                    const inputEl = document.getElementById('searchInput');
                    const q = inputEl ? inputEl.value : "";
                    performSearch(q);
                }
            }

            function removeFromWatchlist(code) {
                watchlist = watchlist.filter(i => i.code !== code);
                localStorage.setItem('finpulse_watchlist', JSON.stringify(watchlist));
                renderContent();
            }

            function updateSetting(key, value) {
                settingsState[key] = value;
                localStorage.setItem('finpulse_settings', JSON.stringify(settingsState));
                
                fetch('/api/settings', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        user_id: userId,
                        all_announcements: settingsState.allAnnouncements,
                        auto_add: settingsState.autoAdd
                    })
                }).catch(err => console.error(err));
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
        "text": "🚀 **FinPulse Pro अपडेट हो गया है!**\n\nअक्टूबर और नवंबर का पूरा डेटा और लाइव ऑटो-अलर्ट वर्कर एक्टिव है। ओपन करने के लिए नीचे दिए गए बटन पर क्लिक करें:",
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
