import os
import requests
import json
from datetime import datetime, timedelta, timezone
import traceback
from quant_engine import build_pre_news_quant
from ai_decider import get_ai_decision

# ====================================================
# DAFTAR SKENARIO BACKTEST (JULI 2026)
# ====================================================
SCENARIOS = [
    {
        "title": "Non-Farm Employment Change",
        "forecast": 200.0,
        "previous": 150.0,
        "date_utc": "2026-07-03 12:30:00",
        "supporting": {
            "ADP Non-Farm Employment Change": {"forecast": 180.0, "previous": 160.0}
        },
        "dxy_change": 0.40,
        "oil_change": 1.0
    },
    {
        "title": "CPI m/m",
        "forecast": 0.3,
        "previous": 0.4,
        "date_utc": "2026-07-14 12:30:00",
        "supporting": {
            "Core CPI m/m": {"forecast": 0.3, "previous": 0.3},
            "PPI m/m": {"forecast": 0.2, "previous": 0.2},
            "Average Hourly Earnings m/m": {"forecast": 0.3, "previous": 0.3}
        },
        "dxy_change": -0.30,
        "oil_change": -2.0
    }
]
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
    send_telegram("⏳ *Memulai Backtest (Twelve Data - T+5m): Juli 2026 (NFP & CPI)*...")
    
    for scen in SCENARIOS:
        try:
            print(f"\n=== MENGUJI SKENARIO: {scen['title']} ({scen['date_utc']}) ===")
            news_dt = datetime.strptime(scen['date_utc'], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            
            price_before = get_price_at_time_twelvedata(news_dt, -5)
            price_after = get_price_at_time_twelvedata(news_dt, 5)
            
            if not price_before or not price_after:
                send_telegram(f"❌ Gagal ambil data historis Gold untuk {scen['title']}.")
                continue

            quant_context = build_pre_news_quant(scen['title'], scen['forecast'], scen['previous'], scen['supporting'])
            market_context = {"dxy_change_pct": scen['dxy_change'], "oil_change_5d_pct": scen['oil_change']}

            decision = get_ai_decision(scen['title'], quant_context, market_context)
            
            if not decision or decision.get('signal') == "ERROR":
                error_msg = decision.get('math_explanation', 'Unknown Error') if decision else 'Gagal API Groq'
                send_telegram(f"❌ *AI Error ({scen['title']}):*\n{error_msg}")
                continue

            ai_signal = decision['signal']
            price_moved_up = price_after > price_before
            actual_direction = "BUY" if price_moved_up else "SELL"
            status_benar = "✅ BENAR" if ai_signal == actual_direction else ("🤷‍♂️ NO TRADE" if ai_signal == "NO TRADE" else "❌ SALAH")
            
            msg = f"""
🧪 *HASIL BACKTEST JULI 2026*
📅 Event: {scen['title']}

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
            print(f"Backtest {scen['title']} Selesai!")

        except Exception as e:
            error_trace = traceback.format_exc()
            print(error_trace)
            send_telegram(f"💥 *Script Crash di {scen['title']}:*\n```\n{error_trace[-300:]}\n```")

if __name__ == "__main__":
    run_backtest()
