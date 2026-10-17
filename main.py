import os
import requests
from macro_fetcher import get_news_and_cluster, get_market_context
from quant_engine import build_pre_news_quant
from ai_decider import get_ai_decision

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"})

def run_agent():
    print("Memulai Analisa Macro Quant...")
    main_event, supporting_data = get_news_and_cluster()
    
    # 1. KALAU GAK ADA BERITA, KIRIM STATUS KE TELEGRAM
    if not main_event:
        print("Tidak ada berita High Impact USD hari ini (WIB).")
        send_telegram("🔍 *Hasil Pengecekan:*\nHari ini tidak ada berita High Impact USD di Forex Factory. Belum ada sinyal untuk XAUUSD.")
        return

    market_context = get_market_context()
    
    quant_context = build_pre_news_quant(
        main_event['title'], 
        main_event['forecast'], 
        main_event['previous'], 
        supporting_data
    )
    
    decision = get_ai_decision(main_event['title'], quant_context, market_context['dxy_change_pct'])
    
    # 2. KALAU ADA BERITA & AI NGASIH SINYAL
    if decision:
        msg = f"""
🌍 *MACRO QUANT PREDICTION*
📅 Event: {main_event['title']}
⏰ Rilis: {main_event['wib_time']} WIB
📊 Forecast: {main_event['forecast']} | Prev: {main_event['previous']}

🧮 *Surprise Score (S_t): {quant_context['main_surprise_score']}*

📉 *Skor Pendukung:*
{chr(10).join([f"- {k}: {v}" for k, v in quant_context['supporting_analysis'].items()]) if quant_context['supporting_analysis'] else "- Tidak ada data pendukung"}

🎯 *PREDIKSI: {decision['signal']}*
🔥 Confidence: {decision['confidence']}
🧠 Logika Math: {decision['math_explanation']}

💡 *Saran Eksekusi:* {decision['trade_plan']}
"""
        send_telegram(msg)
        print(f"Sinyal {main_event['title']} terkirim!")

if __name__ == "__main__":
    run_agent()
