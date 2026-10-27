import os
import requests
import yfinance as yf
import pandas as pd
from datetime import datetime, timezone, timedelta

TWELVE_DATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY")

def get_ff_calendar():
    url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
    try:
        return requests.get(url).json()
    except:
        return []

def clean_float(val):
    if val is None or val == "": return 0.0
    val_str = str(val).replace('%', '').replace(',', '').strip()
    try:
        return float(val_str)
    except:
        return 0.0

def get_news_and_cluster():
    calendar = get_ff_calendar()
    
    wib_tz = timezone(timedelta(hours=7))
    today_wib = datetime.now(wib_tz).date()
    
    target_dates = [today_wib, today_wib + timedelta(days=1), today_wib + timedelta(days=2)]
    upcoming_events = []
    
    # 1. Cari Berita Utama (High Impact) untuk 3 hari ke depan
    for n in calendar:
        if n['country'] != 'USD' or n['impact'] != 'High': continue
        try:
            dt_obj = datetime.fromisoformat(n['date'])
            dt_wib = dt_obj.astimezone(wib_tz)
            
            if dt_wib.date() in target_dates:
                n['wib_time'] = dt_wib.strftime("%H:%M")
                n['wib_date'] = dt_wib.strftime("%Y-%m-%d")
                n['event_date'] = dt_wib.date()
                n['forecast'] = clean_float(n.get('forecast'))
                n['previous'] = clean_float(n.get('previous'))
                upcoming_events.append(n)
        except:
            continue
            
    if not upcoming_events: return []

    processed_events = []
    
    # Daftar Indikator Makro Utama (Dashboard Ekonomi)
    macro_keywords = [
        "CPI", "Core CPI", "PPI", "Core PPI", "PCE", "Core PCE",
        "Non-Farm", "ADP", "Unemployment", "Jobless", "Average Hourly",
        "GDP", "Retail Sales", "ISM", "PMI"
    ]
    
    for main_event in upcoming_events:
        main_title = main_event['title']
        supporting_data = {}
        
        # 2. Cari data makro terbaru untuk semua indikator penting
        for news in calendar:
            if news['country'] != 'USD': continue
            
            title = news['title']
            # Cek apakah termasuk indikator penting
            is_macro = any(k.lower() in title.lower() for k in macro_keywords)
            if not is_macro: continue
            
            # Skip berita utama agar tidak duplikat
            if title == main_title: continue
            
            try:
                news_dt = datetime.fromisoformat(news['date'])
                news_wib = news_dt.astimezone(wib_tz)
                
                act = clean_float(news.get('actual'))
                fcst = clean_float(news.get('forecast'))
                prev = clean_float(news.get('previous'))
                
                # Simpan data terbaru. (Karena di-loop dari awal minggu, data paling akhir akan menimpa data lama)
                supporting_data[title] = {
                    "actual": act,
                    "forecast": fcst,
                    "previous": prev,
                    "date": news_wib.strftime("%Y-%m-%d")
                }
            except:
                continue
                
        processed_events.append({
            "event": main_event,
            "supporting_data": supporting_data
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
