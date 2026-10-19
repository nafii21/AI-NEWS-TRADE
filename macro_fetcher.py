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
    today_wib_str = datetime.now(wib_tz).strftime("%Y-%m-%d")
    
    today_news = []
    for n in calendar:
        if n['country'] != 'USD': continue
        try:
            dt_obj = datetime.fromisoformat(n['date'])
            dt_wib = dt_obj.astimezone(wib_tz)
            if dt_wib.strftime("%Y-%m-%d") == today_wib_str:
                n['wib_time'] = dt_wib.strftime("%H:%M")
                today_news.append(n)
        except:
            continue

    main_news = [n for n in today_news if n['impact'] == 'High']
    if not main_news: return None, None
        
    main_event = main_news[0]
    main_title = main_event['title']
    
    main_event['forecast'] = float(main_event.get('forecast') or 0)
    main_event['previous'] = float(main_event.get('previous') or 0)
    
    supporting_data = {}
    
    # ====================================================
    # LOGIKA CLUSTERING DATA PENDUKUNG (SUPER LENGKAP)
    # ====================================================
    for news in today_news:
        title = news['title']
        f_val = float(news.get('forecast') or 0)
        p_val = float(news.get('previous') or 0)
        
        # 1. Klaster NFP (Tenaga Kerja)
        if "Non-Farm" in main_title or "NFP" in main_title:
            if any(k in title for k in ["ADP", "Employment", "Jobless", "Unemployment", "Average Hourly", "Earnings", "Wages"]):
                supporting_data[title] = {"forecast": f_val, "previous": p_val}
                
        # 2. Klaster CPI (Inflasi - Cost Push, Wage Push, Demand Pull)
        elif "CPI" in main_title or "Consumer Price" in main_title:
            if any(k in title for k in ["PPI", "Core", "Wage", "Average Hourly", "Earnings", "Employment Cost", "ISM", "Retail Sales", "Consumer Confidence"]):
                supporting_data[title] = {"forecast": f_val, "previous": p_val}
                
        # 3. Klaster FOMC (Suku Bunga + Inflasi & Tenaga Kerja)
        elif "FOMC" in main_title or "Federal Funds" in main_title:
            if any(k in title for k in ["GDP", "Retail Sales", "Non-Farm", "PCE", "CPI", "PPI", "Core", "Employment Cost"]):
                supporting_data[title] = {"forecast": f_val, "previous": p_val}
                
        # 4. Klaster Retail Sales (Penjualan Ritel)
        elif "Retail Sales" in main_title:
            if any(k in title for k in ["Core Retail", "Consumer Confidence", "PPI"]):
                supporting_data[title] = {"forecast": f_val, "previous": p_val}

        # 5. Klaster GDP (Pertumbuhan Ekonomi)
        elif "GDP" in main_title:
            if any(k in title for k in ["Trade Balance", "Inventory", "Retail Sales", "Prelim", "Final"]):
                supporting_data[title] = {"forecast": f_val, "previous": p_val}
                
    return main_event, supporting_data

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
