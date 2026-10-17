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

    # Cari News Utama (High Impact)
    main_news = [n for n in today_news if n['impact'] == 'High']
    
    if not main_news:
        return None, None
        
    main_event = main_news[0]
    main_title = main_event['title']
    
    main_event['forecast'] = float(main_event.get('forecast') or 0)
    main_event['previous'] = float(main_event.get('previous') or 0)
    
    supporting_data = {}
    
    # ==========================================
    # LOGIKA CLUSTERING DATA PENDUKUNG
    # ==========================================
    for news in today_news:
        title = news['title']
        f_val = float(news.get('forecast') or 0)
        p_val = float(news.get('previous') or 0)
        
        # 1. Jika News Utama NFP -> Cari ADP, Jobless, Employment
        if "Non-Farm" in main_title or "NFP" in main_title:
            if "ADP" in title or "Employment" in title or "Jobless" in title:
                supporting_data[title] = {"forecast": f_val, "previous": p_val}
                
        # 2. Jika News Utama CPI -> Cari PPI, Core CPI, Upah (Wage)
        elif "CPI" in main_title or "Consumer Price" in main_title:
            if "PPI" in title or "Core" in title or "Wage" in title or "Average Hourly" in title:
                supporting_data[title] = {"forecast": f_val, "previous": p_val}
                
        # 3. Jika News Utama FOMC -> Cari GDP, Retail Sales, NFP
        elif "FOMC" in main_title or "Federal Funds" in main_title:
            if "GDP" in title or "Retail Sales" in title or "Non-Farm" in title:
                supporting_data[title] = {"forecast": f_val, "previous": p_val}
                
        # 4. Jika News Utama GDP -> Cari Trade Balance, Inventories
        elif "GDP" in main_title:
            if "Trade Balance" in title or "Inventory" in title:
                supporting_data[title] = {"forecast": f_val, "previous": p_val}

    return main_event, supporting_data

def get_market_context():
    try:
        # Ambil DXY
        dxy = yf.download("DX-Y.NYB", period="1d", interval="5m", progress=False)
        dxy_change = round(((dxy['Close'].iloc[-1] - dxy['Open'].iloc[0]) / dxy['Open'].iloc[0]) * 100, 2)
        
        # Ambil Minyak (Penting buat konteks CPI/Inflasi)
        oil = yf.download("CL=F", period="5d", interval="1d", progress=False)
        oil_change = round(((oil['Close'].iloc[-1] - oil['Close'].iloc[-5]) / oil['Close'].iloc[-5]) * 100, 2)
        
        return {
            "dxy_change_pct": dxy_change,
            "oil_change_5d_pct": oil_change
        }
    except:
        return {"dxy_change_pct": 0.0, "oil_change_5d_pct": 0.0}
