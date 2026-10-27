import os
import requests
import yfinance as yf
import pandas as pd
from datetime import datetime, timezone, timedelta

TWELVE_DATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY")
FXMACRODATA_BASE = "https://api.fxmacrodata.com/v1"

def clean_float(val):
    if val is None or val == "": return 0.0
    val_str = str(val).replace('%', '').replace(',', '').strip()
    try:
        return float(val_str)
    except:
        return 0.0

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

def get_historical_indicator(indicator_slug):
    url = f"{FXMACRODATA_BASE}/announcements/usd/{indicator_slug}?limit=30"
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, dict) and 'data' in data:
                return data['data']
            elif isinstance(data, list):
                return data
        return []
    except Exception as e:
        print(f"[FXMACRO ERROR] {indicator_slug}: {e}")
        return []

def get_macro_dashboard():
    indicators = {
        "inflation": "CPI",
        "core_inflation": "Core CPI",
        "ppi": "PPI",
        "pce": "PCE",
        "core_pce": "Core PCE",
        "gdp": "GDP"
    }
    
    dashboard = {}
    
    for slug, display_name in indicators.items():
        data = get_historical_indicator(slug)
        if not data:
            print(f"[DEBUG] Data kosong untuk {slug}")
            continue
            
        try:
            data_sorted = sorted(data, key=lambda x: x.get('date', ''), reverse=True)
            latest = data_sorted[0]
        except Exception as e:
            latest = data[0]
            
        # --- PERBAIKAN: Cek semua kemungkinan nama key buat Forecast ---
        act = clean_float(latest.get('val') or latest.get('actual') or latest.get('value'))
        fcst = clean_float(latest.get('consensus') or latest.get('forecast') or latest.get('forecast_value') or latest.get('estimate'))
        prev = clean_float(latest.get('previous') or latest.get('prev'))
        
        # Print buat mastiin di log GitHub
        print(f"[FXMACRO DEBUG] {display_name} | Act: {act} | Fcst: {fcst} | Date: {latest.get('date')}")
        
        if act != 0:
            dashboard[display_name] = {
                "actual": act,
                "forecast": fcst,
                "previous": prev,
                "date": latest.get('date', '')[:10]
            }
            
    return dashboard

def get_news_and_cluster():
    print("Mengambil jadwal berita dari Forex Factory...")
    upcoming_events = get_ff_upcoming_events()
    
    if not upcoming_events: 
        return []
    
    print("Mengambil data Actual dari FXMacroData...")
    macro_dashboard = get_macro_dashboard()
    
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
