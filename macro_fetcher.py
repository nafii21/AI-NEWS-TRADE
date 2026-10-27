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
# 1. JADWAL RILIS 3 HARI KE DEPAN (Forex Factory)
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
# 2. AMBIL DATA HISTORIS (Actual & Forecast Terpisah)
# ==========================================
def get_historical_indicator(indicator_slug):
    # A. Ambil Actual & Previous dari /announcements
    url_ann = f"{FXMACRODATA_BASE}/announcements/usd/{indicator_slug}?limit=30"
    data_actual = []
    try:
        resp = requests.get(url_ann, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, dict) and 'data' in data:
                data_actual = data['data']
    except Exception as e:
        print(f"[FXMACRO ERROR Announcements] {indicator_slug}: {e}")

    # B. Ambil Forecast dari /predictions
    url_pred = f"{FXMACRODATA_BASE}/predictions/usd/{indicator_slug}?prediction_type=market_consensus&limit=30"
    data_pred = []
    try:
        resp = requests.get(url_pred, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, dict) and 'data' in data:
                data_pred = data['data']
    except Exception as e:
        print(f"[FXMACRO ERROR Predictions] {indicator_slug}: {e}")
        
    return data_actual, data_pred

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
    today = datetime.now().date()
    
    for slug, display_name in indicators.items():
        actuals, predictions = get_historical_indicator(slug)
        
        if not actuals:
            continue
            
        # Bikin mapping prediksi berdasarkan tanggal biar gampang dicocokin
        pred_map = {}
        for p in predictions:
            # Ambil predicted_value dari list prediksi (biasanya yang pertama)
            preds = p.get('predictions', [])
            if preds and len(preds) > 0:
                pred_map[p.get('date')] = clean_float(preds[0].get('predicted_value'))
                
        # Filter actual yang udah rilis & urutkan
        valid_data = []
        for item in actuals:
            date_str = item.get('date', '')[:10]
            try:
                item_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                if item_date <= today:
                    item['parsed_date'] = item_date
                    item['date_str'] = date_str
                    valid_data.append(item)
            except:
                continue
                
        if not valid_data:
            continue
            
        valid_data.sort(key=lambda x: x['parsed_date'], reverse=True)
        latest = valid_data[0]
        
        act = clean_float(latest.get('val'))
        prev = clean_float(latest.get('previous_value'))
        # Cocokin forecast berdasarkan tanggal rilis actual
        fcst = pred_map.get(latest.get('date_str'), 0.0)
        
        print(f"[FXMACRO RAW] {display_name} ({latest.get('date_str')}): Act={act}, Fcst={fcst}, Prev={prev}")
        
        if act != 0:
            dashboard[display_name] = {
                "actual": act,
                "forecast": fcst,
                "previous": prev,
                "date": latest.get('date_str')
            }
            
    print(f"[FXMACRO] Berhasil ambil {len(dashboard)} data makro.")
    return dashboard

# ==========================================
# 3. GABUNGIN JADWAL & DATA HISTORIS
# ==========================================
def get_news_and_cluster():
    print("Mengambil jadwal berita dari Forex Factory...")
    upcoming_events = get_ff_upcoming_events()
    
    if not upcoming_events: 
        return []
    
    print("Mengambil data Actual & Forecast dari FXMacroData...")
    macro_dashboard = get_macro_dashboard()
    
    processed_events = []
    for main_event in upcoming_events:
        processed_events.append({
            "event": main_event,
            "supporting_data": macro_dashboard
        })
        
    return processed_events

# ==========================================
# 4. KONTEKS MARKET
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
