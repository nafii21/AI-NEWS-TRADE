import os
import requests
from macro_fetcher import get_news_and_cluster, get_market_context
from quant_engine import build_pre_news_quant
from ai_decider import get_ai_decision

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(msg):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID: return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
    except: pass

def run_agent():
    print("Memulai Analisa Live (Twelve Data)...")
    main_event, supporting_data = get_news_and_cluster()
    
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
    
    decision = get_ai_decision(main_event['title'], quant_context, market_context)
    
    if not decision or decision.get('signal') == "ERROR":
        error_msg = decision.get('math_explanation', 'Unknown Error') if decision else 'Gagal API Groq'
        send_telegram(f"❌ *AI Error:*\n{error_msg}")
        return

    ai_signal = decision['signal']
    
    msg = f"""
🌍 *MACRO QUANT PREDICTION (LIVE)*
📅 Event: {main_event['title']}
⏰ Rilis: {main_event['wib_time']} WIB
📊 Forecast: {main_event['forecast']} | Prev: {main_event['previous']}

🧮 *Surprise Score (S_t): {quant_context['main_surprise_score']}*
📉 *Skor Pendukung:*
{chr(10).join([f"- {k}: {v}" for k, v in quant_context['supporting_analysis'].items()]) if quant_context['supporting_analysis'] else "- Tidak ada data pendukung"}

🌍 *Market (Twelve Data):*
- Harga Gold: ${market_context['gold_price']:.2f}
- DXY: {market_context['dxy_change_pct']}%
- Minyak (Daily): {market_context['oil_change_5d_pct']}%

🎯 *PREDIKSI: {decision['signal']}*
🔥 Confidence: {decision['confidence']}
🧠 Logika: {decision['math_explanation']}

💡 *Saran Eksekusi:* {decision['trade_plan']}
"""
    send_telegram(msg)
    print("Sinyal Live terkirim!")

if __name__ == "__main__":
    run_agent()
