import os
import requests
import yfinance as yf
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
    
    # Scan 3 hari ke depan (Hari ini, Besok, Lusa)
    target_dates = [today_wib, today_wib + timedelta(days=1), today_wib + timedelta(days=2)]
    
    upcoming_events = []
    
    for n in calendar:
        if n['country'] != 'USD' or n['impact'] != 'High': continue
        try:
            dt_obj = datetime.fromisoformat(n['date'])
            dt_wib = dt_obj.astimezone(wib_tz)
            
            if dt_wib.date() in target_dates:
                n['wib_time'] = dt_wib.strftime("%H:%M")
                n['wib_date'] = dt_wib.strftime("%Y-%m-%d")
                n['event_date'] = dt_wib.date()
                upcoming_events.append(n)
        except:
            continue
            
    if not upcoming_events: return []

    processed_events = []
    
    for main_event in upcoming_events:
        main_title = main_event['title']
        event_date = main_event['event_date']
        
        main_event['forecast'] = clean_float(main_event.get('forecast'))
        main_event['previous'] = clean_float(main_event.get('previous'))
        
        supporting_data = {}
        for news in calendar:
            if news['country'] != 'USD': continue
            try:
                news_dt = datetime.fromisoformat(news['date'])
                news_wib = news_dt.astimezone(wib_tz)
                
                if news_wib.date() != event_date: continue
                if news['title'] == main_title: continue
                    
                title = news['title']
                f_val = clean_float(news.get('forecast'))
                p_val = clean_float(news.get('previous'))
                
                if "Non-Farm" in main_title or "NFP" in main_title:
                    if any(k in title for k in ["ADP", "Employment", "Jobless", "Unemployment", "Average Hourly", "Earnings", "Wages"]):
                        supporting_data[title] = {"forecast": f_val, "previous": p_val}
                elif "CPI" in main_title or "Consumer Price" in main_title:
                    if any(k in title for k in ["PPI", "Core", "Wage", "Average Hourly", "Earnings", "Employment Cost", "ISM", "Retail Sales", "Consumer Confidence"]):
                        supporting_data[title] = {"forecast": f_val, "previous": p_val}
                elif "FOMC" in main_title or "Federal Funds" in main_title:
                    if any(k in title for k in ["GDP", "Retail Sales", "Non-Farm", "PCE", "CPI", "PPI", "Core", "Employment Cost"]):
                        supporting_data[title] = {"forecast": f_val, "previous": p_val}
                elif "Retail Sales" in main_title:
                    if any(k in title for k in ["Core Retail", "Consumer Confidence", "PPI"]):
                        supporting_data[title] = {"forecast": f_val, "previous": p_val}
                elif "GDP" in main_title:
                    if any(k in title for k in ["Trade Balance", "Inventory", "Retail Sales", "Prelim", "Final"]):
                        supporting_data[title] = {"forecast": f_val, "previous": p_val}
            except:
                continue
                
        processed_events.append({
            "event": main_event,
            "supporting_data": supporting_data
        })
        
    return processed_events

def get_twelve_data_gold():
    # Ambil harga Gold dari Twelve Data
    url = f"https://api.twelvedata.com/quote?symbol=XAU/USD&apikey={TWELVE_DATA_API_KEY}"
    try:
        resp = requests.get(url, timeout=10).json()
        if "close" in resp:
            return float(resp["close"])
    except:
        pass
    return 0.0

def get_market_context():
    # 1. Gold dari Twelve Data
    gold_price = get_twelve_data_gold()
    
    # 2. DXY & Minyak dari yfinance (karena Twelve Data limitasi simbol)
    try:
        # DXY (Daily change)
        dxy = yf.download("DX-Y.NYB", period="5d", interval="1d", progress=False)
        if not dxy.empty:
            dxy_change = ((dxy['Close'].iloc[-1] - dxy['Close'].iloc[-2]) / dxy['Close'].iloc[-2]) * 100
        else:
            dxy_change = 0.0
            
        # Minyak (Daily change 5 hari)
        oil = yf.download("CL=F", period="10d", interval="1d", progress=False)
        if len(oil) >= 5:
            oil_change = ((oil['Close'].iloc[-1] - oil['Close'].iloc[-5]) / oil['Close'].iloc[-5]) * 100
        else:
            oil_change = 0.0
    except Exception as e:
        print(f"Error yfinance: {e}")
        dxy_change = 0.0
        oil_change = 0.0
    
    return {
        "dxy_change_pct": round(float(dxy_change), 2),
        "oil_change_5d_pct": round(float(oil_change), 2),
        "gold_price": gold_price
    }
