import requests
import yfinance as yf
from datetime import datetime, timezone, timedelta

def get_ff_calendar():
    url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
    try:
        return requests.get(url).json()
    except:
        return []

def get_news_and_cluster():
    calendar = get_ff_calendar()
    
    # Pakai zona waktu WIB (UTC+7)
    wib_tz = timezone(timedelta(hours=7))
    today_wib_str = datetime.now(wib_tz).strftime("%Y-%m-%d")
    
    today_news = []
    for n in calendar:
        if n['country'] != 'USD': continue
        
        try:
            # Forex Factory ngasih format ISO 8601 (misal: 2024-05-03T08:30:00-04:00)
            dt_str = n['date']
            dt_obj = datetime.fromisoformat(dt_str)
            
            # Konversi ke WIB
            dt_wib = dt_obj.astimezone(wib_tz)
            
            # Cek apakah tanggal rilis (dalam WIB) sama dengan hari ini
            if dt_wib.strftime("%Y-%m-%d") == today_wib_str:
                n['wib_time'] = dt_wib.strftime("%H:%M") # Simpan jam WIB
                today_news.append(n)
        except:
            continue

    main_news = [n for n in today_news if n['impact'] == 'High']
    
    if not main_news:
        return None, None
        
    main_event = main_news[0]
    main_title = main_event['title']
    
    # Pastiin angkanya float
    main_event['forecast'] = float(main_event.get('forecast') or 0)
    main_event['previous'] = float(main_event.get('previous') or 0)
    
    supporting_data = {}
    for news in today_news:
        title = news['title']
        if "Non-Farm" in main_title:
            if "ADP" in title or "Employment" in title or "Jobless" in title:
                supporting_data[title] = {
                    "forecast": float(news.get('forecast') or 0),
                    "previous": float(news.get('previous') or 0)
                }
    return main_event, supporting_data

def get_market_context():
    try:
        dxy = yf.download("DX-Y.NYB", period="1d", interval="5m", progress=False)
        return {
            "dxy_change_pct": round(((dxy['Close'].iloc[-1] - dxy['Open'].iloc[0]) / dxy['Open'].iloc[0]) * 100, 2)
        }
    except:
        return {"dxy_change_pct": 0.0}
