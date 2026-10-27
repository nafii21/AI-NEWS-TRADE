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

def get_fmp_calendar():
    today = datetime.now(timezone.utc)
    from_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
    to_date = (today + timedelta(days=3)).strftime("%Y-%m-%d")
    
    url = f"https://financialmodelingprep.com/api/v3/economic_calendar?from={from_date}&to={to_date}&apikey={FMP_API_KEY}"
    try:
        resp = requests.get(url, timeout=20).json()
        
        # --- PENGAMAN: Cek apakah responnya list (data beneran) atau dict (pesan error) ---
        if not isinstance(resp, list):
            print(f"FMP API ERROR: {resp}")
            return [] 
            
        return resp
    except Exception as e:
        print(f"Error fetching FMP: {e}")
        return []

def get_news_and_cluster():
    calendar = get_fmp_calendar()
    if not calendar: return []
    
    wib_tz = timezone(timedelta(hours=7))
    today_wib = datetime.now(wib_tz).date()
    target_dates = [today_wib, today_wib + timedelta(days=1), today_wib + timedelta(days=2)]
    
    macro_keywords = ["CPI", "PPI", "PCE", "Non-Farm", "NFP", "ADP", "Unemployment", "GDP", "Retail Sales", "ISM"]
    upcoming_events = []
    macro_dashboard = {}
    
    for n in calendar:
        # Pengaman tambahan: pastikan n itu dictionary
        if not isinstance(n, dict): continue
        
        country = n.get('country', '')
        if country not in ['US', 'USD']: continue
        
        event_name = n.get('event', '')
        impact = n.get('impact', '')
        
        act = clean_float(n.get('actual'))
        fcst = clean_float(n.get('estimate'))
        prev = clean_float(n.get('prev'))
        
        # 1. Cari Berita Utama (High Impact) untuk 3 hari ke depan
        if impact == 'High' or impact == 'high':
            try:
                dt_obj = datetime.fromisoformat(n['date'])
                dt_wib = dt_obj.astimezone(wib_tz)
                if dt_wib.date() in target_dates:
                    n['wib_time'] = dt_wib.strftime("%H:%M")
                    n['wib_date'] = dt_wib.strftime("%Y-%m-%d")
                    n['forecast'] = fcst
                    n['previous'] = prev
                    upcoming_events.append(n)
            except: continue
            
        # 2. Kumpulkan Dashboard Makro (Actual terbaru)
        is_macro = any(k.lower() in event_name.lower() for k in macro_keywords)
        if is_macro and act != 0:
            date_str = n.get('date', '')[:10]
            if event_name not in macro_dashboard or date_str > macro_dashboard[event_name]['date']:
                macro_dashboard[event_name] = {
                    "actual": act,
                    "forecast": fcst,
                    "previous": prev,
                    "date": date_str
                }

    if not upcoming_events: return []

    processed_events = []
    for main_event in upcoming_events:
        processed_events.append({
            "event": main_event,
            "supporting_data": macro_dashboard
        })
        
    return processed_events

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
