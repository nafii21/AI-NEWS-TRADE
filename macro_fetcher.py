import os
import requests
import yfinance as yf
import pandas as pd
from datetime import datetime, timezone, timedelta

TWELVE_DATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY")
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

def clean_float(val):
    if val is None or val == "": return 0.0
    val_str = str(val).replace('%', '').replace(',', '').strip()
    try:
        return float(val_str)
    except:
        return 0.0

def get_finnhub_calendar():
    """Narik kalender ekonomi dari 30 hari lalu sampai 3 hari ke depan"""
    today = datetime.now()
    start_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
    end_date = (today + timedelta(days=3)).strftime("%Y-%m-%d")
    
    url = f"https://finnhub.io/api/v1/calendar/economic?from={start_date}&to={end_date}&token={FINNHUB_API_KEY}"
    try:
        resp = requests.get(url, timeout=15).json()
        return resp.get("economicCalendar", [])
    except:
        return []

def get_news_and_cluster():
    calendar = get_finnhub_calendar()
    
    wib_tz = timezone(timedelta(hours=7))
    today_wib = datetime.now(wib_tz).date()
    
    target_dates = [today_wib, today_wib + timedelta(days=1), today_wib + timedelta(days=2)]
    
    # Indikator Makro Utama yang WAJIB dilacak
    macro_keywords = [
        "CPI", "PPI", "PCE", "Non-Farm", "NFP", "ADP", 
        "Unemployment", "GDP", "Retail Sales", "ISM"
    ]
    
    # 1. Kumpulkan semua data historis & data masa depan
    macro_dashboard = {}
    upcoming_events = []
    
    for n in calendar:
        if n.get('country') != 'US': continue
        event_name = n.get('event', '')
        impact = n.get('impact', '').lower()
        
        # Simpan data masa depan untuk Fase 1
        if impact == 'high':
            try:
                dt_obj = datetime.fromisoformat(n['date'] + 'T' + n.get('time', '00:00:00'))
                dt_wib = dt_obj.astimezone(wib_tz)
                if dt_wib.date() in target_dates:
                    n['wib_time'] = dt_wib.strftime("%H:%M")
                    n['wib_date'] = dt_wib.strftime("%Y-%m-%d")
                    n['forecast'] = clean_float(n.get('estimate'))
                    n['previous'] = clean_float(n.get('prev'))
                    upcoming_events.append(n)
            except:
                continue
                
        # Simpan semua data makro terbaru ke Dashboard
        is_macro = any(k.lower() in event_name.lower() for k in macro_keywords)
        if is_macro:
            act = clean_float(n.get('actual'))
            fcst = clean_float(n.get('estimate'))
            prev = clean_float(n.get('prev'))
            
            # Kalo datanya lebih baru, timpa yang lama
            if event_name not in macro_dashboard or n['date'] > macro_dashboard[event_name]['date']:
                macro_dashboard[event_name] = {
                    "actual": act,
                    "forecast": fcst,
                    "previous": prev,
                    "date": n['date']
                }

    if not upcoming_events: return []

    processed_events = []
    
    # 2. Gabungkan Berita Utama dengan Dashboard Makro terbaru
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
