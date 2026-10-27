import os
import requests
from datetime import datetime, timezone, timedelta

TWELVE_DATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY")

def get_ff_calendar():
    url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
    try:
        return requests.get(url).json()
    except:
        return []

def get_news_and_cluster():
    calendar = get_ff_calendar()
    
    wib_tz = timezone(timedelta(hours=7))
    today_wib = datetime.now(wib_tz).date()
    
    # Scan untuk hari ini, besok, dan lusa (3 hari)
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
                upcoming_events.append(n)
        except:
            continue
            
    if not upcoming_events: return []

    processed_events = []
    
    # 2. Untuk setiap berita utama, cari data pendukung di hari yang SAMA
    for main_event in upcoming_events:
        main_title = main_event['title']
        event_date = main_event['event_date']
        
        main_event['forecast'] = float(main_event.get('forecast') or 0)
        main_event['previous'] = float(main_event.get('previous') or 0)
        
        supporting_data = {}
        for news in calendar:
            if news['country'] != 'USD': continue
            try:
                news_dt = datetime.fromisoformat(news['date'])
                news_wib = news_dt.astimezone(wib_tz)
                
                # Cari data pendukung HANYA di tanggal yang sama dengan berita utama
                if news_wib.date() != event_date: continue
                if news['title'] == main_title: continue
                    
                title = news['title']
                f_val = float(news.get('forecast') or 0)
                p_val = float(news.get('previous') or 0)
                
                # Logika Clustering (Sama seperti sebelumnya)
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

def get_twelve_data_quote(symbol):
    url = f"https://api.twelvedata.com/quote?symbol={symbol}&apikey={TWELVE_DATA_API_KEY}"
    try:
        resp = requests.get(url, timeout=10).json()
        if "close" in resp:
            return {
                "price": float(resp["close"]),
                "change_pct": float(resp.get("percent_change", 0.0))
            }
    except:
        pass
    return None

def get_market_context():
    dxy_data = get_twelve_data_quote("DXY")
    oil_data = get_twelve_data_quote("WTI/USD")
    gold_data = get_twelve_data_quote("XAU/USD")
    
    return {
        "dxy_change_pct": dxy_data["change_pct"] if dxy_data else 0.0,
        "oil_change_5d_pct": oil_data["change_pct"] if oil_data else 0.0,
        "gold_price": gold_data["price"] if gold_data else 0.0
    }
