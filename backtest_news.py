import os
import requests
import json
import time
from datetime import datetime, timedelta, timezone
import traceback
from quant_engine import build_pre_news_quant
from ai_decider import get_ai_decision
from manual_macro import MANUAL_DASHBOARD

# ====================================================
# SKENARIO BACKTEST: NFP 7 AGUSTUS 2026
# ====================================================
SCENARIOS = [
    {
        "title": "NFP (Non-Farm Payrolls)",
        "forecast": 63.0,
        "previous": 29.0,
        "date_utc": "2026-11-06 12:30:00",
        "supporting": MANUAL_DASHBOARD,
        "dxy_change": 0.0,
        "oil_change": 0.0
    }
]

TWELVE_DATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY")
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
    start_date = (target_time - timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:00")
    end_date = (target_time + timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:00")
    
    url = "https://api.twelvedata.com/time_series"
    params = {
        "symbol": "XAU/USD", "interval": "1min",
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
    send_telegram("⏳ *Memulai Backtest (Bebas Bocoran): NFP 7 Agustus 2026*...")
    
    for i, scen in enumerate(SCENARIOS, 1):
        try:
            news_dt = datetime.strptime(scen['date_utc'], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            
            price_before = get_price_at_time_twelvedata(news_dt, -5)
            time.sleep(8)
            price_after = get_price_at_time_twelvedata(news_dt, 5)
            time.sleep(8)
            
            if not price_before or not price_after:
                send_telegram(f"❌ Gagal ambil harga untuk {scen['title']}.")
                continue

            quant_context = build_pre_news_quant(scen['title'], scen['forecast'], scen['previous'], scen['supporting'])
            market_context = {"dxy_change_pct": scen['dxy_change'], "oil_change_5d_pct": scen['oil_change']}

            decision = get_ai_decision(scen['title'], quant_context, market_context)
            
            if not decision or decision.get('signal') == "ERROR":
                send_telegram(f"❌ *AI Error:* {decision.get('math_explanation', 'Unknown')}")
                continue

            ai_signal = decision['signal']
            price_moved_up = price_after > price_before
            actual_direction = "BUY" if price_moved_up else "SELL"
            status_benar = "✅ BENAR" if ai_signal == actual_direction else ("🤷‍♂️ NO TRADE" if ai_signal == "NO TRADE" else "❌ SALAH")
            
            msg = f"""
🧪 *HASIL BACKTEST NFP (7 AGU 2026)*
📅 Tanggal Rilis: {scen['date_utc'][:10]}

📊 *Data Gold:*
Sebelum (T-5): ${price_before:.2f}
Sesudah (T+5): ${price_after:.2f}

🎯 *Prediksi AI:* {ai_signal}
🔥 Confidence: {decision['confidence']}
🧠 Alasan: {decision['math_explanation']}

📈 *Realita:* Gold {('NAIK' if price_moved_up else 'TURUN')}
🏁 *Hasil:* {status_benar}
"""
            send_telegram(msg)
            print(f"[DONE] {scen['title']} - {status_benar}")

        except Exception as e:
            print(traceback.format_exc())

if __name__ == "__main__":
    run_backtest()
