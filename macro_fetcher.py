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

# ==========================================
# 1. JADWAL RILIS (FXMacroData Calendar)
# ==========================================
def get_upcoming_events():
    """Narik jadwal rilis USD dari FXMacroData"""
    url = f"{FXMACRODATA_BASE}/calendar/usd"
    try:
        resp = requests.get(url, timeout=15).json()
        # FXMacroData free tier biasanya return list of dict
        if not isinstance(resp, list):
            print(f"[FXMACRO ERROR] Response bukan list: {resp}")
            return []
        return resp
    except Exception as e:
        print(f"[FXMACRO REQUEST ERROR] {e}")
        return []

# ==========================================
# 2. DATA HISTORIS (FXMacroData Announcements)
# ==========================================
def get_historical_indicator(indicator_slug):
    """Narik data historis satu indikator (Actual, Forecast, Previous)"""
    # limit=30 buat narik 30 data terakhir
    url = f"{FXMACRODATA_BASE}/announcements/usd/{indicator_slug}?limit=30"
    try:
        resp = requests.get(url, timeout=15).json()
        if isinstance(resp, list):
            return resp
        return []
    except Exception as e:
        print(f"[FXMACRO ERROR] {indicator_slug}: {e}")
        return []

def get_macro_dashboard():
    """Kumpulkan data Actual terbaru dari indikator makro penting"""
    # Mapping nama indikator ke slug FXMacroData
    # (Slug bisa dilihat di /v1/data_catalogue/usd)
    indicators = {
        "inflation": "CPI",
        "core_inflation": "Core CPI",
        "ppi": "PPI",
        "core_pce": "Core PCE",
        "non_farm_payrolls": "NFP",
        "unemployment": "Unemployment",
        "gdp": "GDP",
        "retail_sales": "Retail Sales",
        "average_hourly_earnings": "AHE"
    }
    
    dashboard = {}
    
    for slug, display_name in indicators.items():
        data = get_historical_indicator(slug)
        if not data:
            continue
            
        # Ambil data paling baru (biasanya index 0)
        latest = data[0]
        
        # Struktur data FXMacroData biasanya: 
        # {"date": "...", "value": ..., "forecast": ..., "previous": ...}
        # Kita sesuaikan dengan key yang mungkin ada
        act = clean_float(latest.get('value') or latest.get('actual'))
        fcst = clean_float(latest.get('forecast') or latest.get('consensus'))
        prev = clean_float(latest.get('previous'))
        
        if act != 0:
            dashboard[display_name] = {
                "actual": act,
                "forecast": fcst,
                "previous": prev,
                "date": latest.get('date', '')[:10]
            }
            
    return dashboard

# ==========================================
# 3. GABUNGIN JADWAL & DATA HISTORIS
# ==========================================
def get_news_and_cluster():
    print("Mengambil jadwal berita dari FXMacroData...")
    all_events = get_upcoming_events()
    
    if not all_events: return []
    
    wib_tz = timezone(timedelta(hours=7))
    today_wib = datetime.now(wib_tz).date()
    target_dates = [today_wib, today_wib + timedelta(days=1), today_wib + timedelta(days=2)]
    
    # Filter berita High Impact untuk 3 hari ke depan
    upcoming_events = []
    for n in all_events:
        if not isinstance(n, dict): continue
        if n.get('country', '').upper() != 'US': continue
        
        # FXMacroData biasanya punya field 'impact' atau 'importance'
        impact = str(n.get('impact', '') or n.get('importance', '')).lower()
        if impact not in ['high', '3', 'red']: continue
        
        try:
            dt_obj = datetime.fromisoformat(n['date'])
            dt_wib = dt_obj.astimezone(wib_tz)
            if dt_wib.date() in target_dates:
                n['wib_time'] = dt_wib.strftime("%H:%M")
                n['wib_date'] = dt_wib.strftime("%Y-%m-%d")
                n['forecast'] = clean_float(n.get('forecast'))
                n['previous'] = clean_float(n.get('previous'))
                upcoming_events.append(n)
        except: continue
        
    if not upcoming_events: return []
    
    print("Mengambil data Actual dari FXMacroData...")
    macro_dashboard = get_macro_dashboard()
    
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
