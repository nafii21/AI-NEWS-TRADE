import os
import requests
import yfinance as yf
import pandas as pd
from datetime import datetime, timezone, timedelta

TWELVE_DATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY")
FMP_API_KEY = os.getenv("FMP_API_KEY")

def clean_float(val):
    if val is None or val == "": return 0.0
    val_str = str(val).replace('%', '').replace(',', '').strip()
    try:
        return float(val_str)
    except:
        return 0.0

# ==========================================
# 1. FUNGSI UNTUK FOREX FACTORY (Jadwal 3 Hari)
# ==========================================
def get_ff_upcoming_events():
    urls = [
        "https://nfs.faireconomy.media/ff_calendar_thisweek.json",
        "https://nfs.faireconomy.media/ff_calendar_nextweek.json"
    ]
    calendar = []
    for url in urls:
        try:
            resp = requests.get(url, timeout=10).json()
            if isinstance(resp, list): calendar.extend(resp)
        except: pass
    
    wib_tz = timezone(timedelta(hours=7))
    today_wib = datetime.now(wib_tz).date()
    target_dates = [today_wib, today_wib + timedelta(days=1), today_wib + timedelta(days=2)]
    
    upcoming = []
    for n in calendar:
        if n.get('country') != 'USD' or n.get('impact', '').lower() != 'high': continue
        try:
            dt_obj = datetime.fromisoformat(n['date'])
            dt_wib = dt_obj.astimezone(wib_tz)
            if dt_wib.date() in target_dates:
                n['wib_time'] = dt_wib.strftime("%H:%M")
                n['wib_date'] = dt_wib.strftime("%Y-%m-%d")
                n['forecast'] = clean_float(n.get('forecast'))
                n['previous'] = clean_float(n.get('previous'))
                upcoming.append(n)
        except: continue
    return upcoming

# ==========================================
# 2. FUNGSI UNTUK FMP (Data Actual 30 Hari)
# ==========================================
def get_fmp_macro_dashboard():
    if not FMP_API_KEY:
        print("FMP_API_KEY tidak ditemukan.")
        return {}
        
    today = datetime.now(timezone.utc)
    from_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
    to_date = today.strftime("%Y-%m-%d")
    
    url = f"https://financialmodelingprep.com/api/v3/economic_calendar?from={from_date}&to={to_date}&apikey={FMP_API_KEY}"
    try:
        resp = requests.get(url, timeout=15).json()
        if not isinstance(resp, list): 
            print(f"FMP Error: {resp}")
            return {}
    except Exception as e:
        print(f"FMP Request Error: {e}")
        return {}

    macro_keywords = ["CPI", "PPI", "PCE", "Non-Farm", "NFP", "ADP", "Unemployment", "GDP", "Retail Sales", "ISM"]
    dashboard = {}
    
    for n in resp:
        if n.get('country') not in ['US', 'USD']: continue
        event_name = n.get('event', '')
        is_macro = any(k.lower() in event_name.lower() for k in macro_keywords)
        
        if is_macro:
            act = clean_float(n.get('actual'))
            if act != 0: # Cuma simpan yang udah rilis
                date_str = n.get('date', '')[:10]
                if event_name not in dashboard or date_str > dashboard[event_name]['date']:
                    dashboard[event_name] = {
                        "actual": act,
                        "forecast": clean_float(n.get('estimate')),
                        "previous": clean_float(n.get('prev')),
                        "date": date_str
                    }
    return dashboard

# ==========================================
# 3. GABUNGIN DUA-DUANYA
# ==========================================
def get_news_and_cluster():
    print("Mengambil jadwal berita dari Forex Factory...")
    upcoming_events = get_ff_upcoming_events()
    
    if not upcoming_events: return []
    
    print("Mengambil data Actual dari FMP...")
    macro_dashboard = get_fmp_macro_dashboard()
    
    processed_events = []
    for main_event in upcoming_events:
        processed_events.append({
            "event": main_event,
            "supporting_data": macro_dashboard
        })
        
    return processed_events

# ==========================================
# 4. KONTEKS MARKET (Twelve Data & YF)
# ==========================================
def get_twelve_data_gold():
    url = f"https://api.twelvedata.com/quote?symbol=XAU/USD&apikey={TWELVE_DATA_API_KEY}"
    try:
        resp = requests.get(url, timeout=10).json()
        if "close" in resp: return float(resp["close"])
    except: pass
    return 0.0

def get_market_context():
    gold_price = get_twelve_data_gold()
    dxy_change = 0.0
    oil_change = 0.0
    try:
        dxy = yf.download("DX-Y.NYB", period="5d", interval="1d", progress=False)
        if not dxy.empty:
            if isinstance(dxy.columns, pd.MultiIndex): dxy.columns = dxy.columns.get_level_values(0)
            if len(dxy) > 1: dxy_change = ((dxy['Close'].iloc[-1] - dxy['Close'].iloc[-2]) / dxy['Close'].iloc[-2]) * 100
        
        oil = yf.download("CL=F", period="10d", interval="1d", progress=False)
        if not oil.empty:
            if isinstance(oil.columns, pd.MultiIndex): oil.columns = oil.columns.get_level_values(0)
            if len(oil) >= 5: oil_change = ((oil['Close'].iloc[-1] - oil['Close'].iloc[-5]) / oil['Close'].iloc[-5]) * 100
    except: pass
    
    return {
        "dxy_change_pct": round(float(dxy_change), 2),
        "oil_change_5d_pct": round(float(oil_change), 2),
        "gold_price": gold_price
    }
