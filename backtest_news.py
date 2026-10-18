import os
import requests
import json
from datetime import datetime, timedelta, timezone
import traceback
from quant_engine import build_pre_news_quant
from ai_decider import get_ai_decision

# ====================================================
# SKENARIO TUNGGAL: CPI 12 AGUSTUS 2026 (LENGKAP)
# ====================================================
NEWS_TITLE = "CPI m/m"
FORECAST = 0.3
PREVIOUS = 0.4
NEWS_DATE_UTC = "2026-08-12 12:30:00"

# SEMUA DATA PENDUKUNG YANG MEMPENGARUHI CPI DIMASUKIN
SUPPORTING_DATA = {
    "Core CPI m/m": {"forecast": 0.3, "previous": 0.3},
    "PPI m/m": {"forecast": 0.2, "previous": 0.2},
    "Average Hourly Earnings m/m": {"forecast": 0.3, "previous": 0.4},
    "Employment Cost Index": {"forecast": 1.1, "previous": 1.2}
}

DXY_CHANGE_PCT = -0.20 
OIL_CHANGE_PCT = -1.5  
# ====================================================

TWELVE_DATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY")
if not TWELVE_DATA_API_KEY:
    raise ValueError("API Key Twelve Data belum di-set.")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(msg):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID: return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
    except: pass

def get_price_at_time_twelvedata(target_dt, offset_minutes):
    target_time = target_dt + timedelta(minutes=offset_minutes)
    start_date = (target_time - timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")
    end_date = (target_time + timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")
    
    url = "https://api.twelvedata.com/time_series"
    params = {
        "symbol": "XAU/USD", "interval": "5min",
        "start_date": start_date, "end_date": end_date,
        "timezone": "UTC", "apikey": TWELVE_DATA_API_KEY, "order": "ASC"
    }
    try:
        response = requests.get(url, params=params, timeout=15).json()
        if response.get("status") == "error": return None
        values = response.get("values", [])
        if not values: return None
        return float(values[0]["close"])
    except: return None

def run_backtest():
    try:
        send_telegram(f"⏳ *Memulai Backtest (Twelve Data - T+5m):* {NEWS_TITLE}...")
        news_dt = datetime.strptime(NEWS_DATE_UTC, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        
        price_before = get_price_at_time_twelvedata(news_dt, -5) 
        price_after = get_price_at_time_twelvedata(news_dt, 5)  
        
        if not price_before or not price_after:
            send_telegram(f"❌ Gagal ambil data historis Gold.")
            return

        quant_context = build_pre_news_quant(NEWS_TITLE, FORECAST, PREVIOUS, SUPPORTING_DATA)
        market_context = {"dxy_change_pct": DXY_CHANGE_PCT, "oil_change_5d_pct": OIL_CHANGE_PCT}

        decision = get_ai_decision(NEWS_TITLE, quant_context, market_context)
        
        if not decision or decision.get('signal') == "ERROR":
            send_telegram(f"❌ *AI Error:*\n{decision.get('math_explanation', 'Unknown')}")
            return

        ai_signal = decision['signal']
        price_moved_up = price_after > price_before
        actual_direction = "BUY" if price_moved_up else "SELL"
        status_benar = "✅ BENAR" if ai_signal == actual_direction else ("🤷‍♂️ NO TRADE" if ai_signal == "NO TRADE" else "❌ SALAH")
        
        msg = f"""
🧪 *HASIL BACKTEST (T+5 Menit)*
📅 Event: {NEWS_TITLE}

📊 *Data Gold:*
Sebelum (T-5): ${price_before:.2f}
Sesudah (T+5): ${price_after:.2f}

🧮 *Kuantitatif:*
- S_t Utama: {quant_context['main_surprise_score']}
- Support: {quant_context['supporting_analysis']}

🎯 *Prediksi AI:* {ai_signal}
🔥 Confidence: {decision['confidence']}
💡 Alasan: {decision['math_explanation']}

📈 *Realita:* Gold {('NAIK' if price_moved_up else 'TURUN')}
🏁 *Hasil:* {status_benar}
"""
        send_telegram(msg)
    except Exception as e:
        print(traceback.format_exc())

if __name__ == "__main__":
    run_backtest()
