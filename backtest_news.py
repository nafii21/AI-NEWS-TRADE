import os
import requests
import json
from datetime import datetime, timezone
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
        "date_utc": "2026-08-07 12:30:00",
        "supporting": MANUAL_DASHBOARD,
        "dxy_change": 0.0,
        "oil_change": 0.0
    }
]

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(msg):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID: return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
    except Exception as e: 
        print(f"Error Telegram: {e}")

def run_backtest():
    send_telegram("⏳ *Memulai Simulasi AI (Tanpa Cek Harga): NFP 7 Agustus 2026*...")
    
    for i, scen in enumerate(SCENARIOS, 1):
        try:
            # Hitung Quant
            quant_context = build_pre_news_quant(scen['title'], scen['forecast'], scen['previous'], scen['supporting'])
            market_context = {"dxy_change_pct": scen['dxy_change'], "oil_change_5d_pct": scen['oil_change']}

            # Tanya AI
            decision = get_ai_decision(scen['title'], quant_context, market_context)
            
            if not decision or decision.get('signal') == "ERROR":
                send_telegram(f"❌ *AI Error:* {decision.get('math_explanation', 'Unknown')}")
                continue

            ai_signal = decision['signal']
            tanggal_rilis = scen['date_utc'][:10]
            
            # Format Pesan Telegram (Tanpa Harga)
            msg = f"""
🧪 *SIMULASI PREDIKSI AI*
📅 Event: {scen['title']}
📆 Tanggal Rilis: {tanggal_rilis}
📊 Forecast: {scen['forecast']} | Prev: {scen['previous']}

🧮 *Skor Kejutan (S_t): {quant_context['main_surprise_score']}*
📉 *Data Makro Pendukung (Historis):*
{chr(10).join([f"  - {k}: {v['desc']} (Skor: {v['score']})" for k, v in quant_context['supporting_analysis'].items()])}

🎯 *PREDIKSI AI:* {ai_signal}
🔥 Confidence: {decision['confidence']}
🧠 Alasan Logis: {decision['math_explanation']}

💡 *Saran Eksekusi:* {decision['trade_plan']}
"""
            send_telegram(msg)
            print(f"[DONE] Simulasi {scen['title']} terkirim ke Telegram.")

        except Exception as e:
            print(traceback.format_exc())

if __name__ == "__main__":
    run_backtest()
