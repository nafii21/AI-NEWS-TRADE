import os
import requests
from datetime import datetime
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
    print("Memulai Analisa Live (Proyeksi 3 Hari)...")
    processed_events = get_news_and_cluster()
    
    today_date = datetime.now().strftime("%Y-%m-%d")
    
    if not processed_events:
        print("Tidak ada berita High Impact USD untuk 3 hari ke depan.")
        send_telegram(f"🔍 *Hasil Pengecekan ({today_date}):*\nTidak ada berita High Impact USD untuk 3 hari ke depan (Hari ini, Besok, Lusa).")
        return

    # Tarik data market hari ini (jadi acuan untuk semua prediksi)
    market_context = get_market_context()
    
    send_telegram(f"🔄 *Memproses {len(processed_events)} Berita Penting (3 Hari Ke Depan)*...")
    
    for item in processed_events:
        main_event = item['event']
        supporting_data = item['supporting_data']
        
        quant_context = build_pre_news_quant(
            main_event['title'], 
            main_event['forecast'], 
            main_event['previous'], 
            supporting_data
        )
        
        decision = get_ai_decision(main_event['title'], quant_context, market_context)
        
        if not decision or decision.get('signal') == "ERROR":
            error_msg = decision.get('math_explanation', 'Unknown Error') if decision else 'Gagal API Groq'
            send_telegram(f"❌ *AI Error ({main_event['title']} - {main_event['wib_date']}):*\n{error_msg}")
            continue

        ai_signal = decision['signal']
        event_title = main_event['title'].replace("Non-Farm Employment Change", "NFP (Non-Farm Payrolls)")
        
        msg = f"""
🌍 *MACRO QUANT PREDICTION (LIVE)*
📆 Tanggal Rilis: {main_event['wib_date']}
📅 Event: {event_title}
⏰ Jam: {main_event['wib_time']} WIB
📊 Forecast: {main_event['forecast']} | Prev: {main_event['previous']}

🧮 *Surprise Score (S_t): {quant_context['main_surprise_score']}*
📉 *Skor Pendukung:*
{chr(10).join([f"- {k}: {v}" for k, v in quant_context['supporting_analysis'].items()]) if quant_context['supporting_analysis'] else "- Tidak ada data pendukung"}

🎯 *PREDIKSI: {decision['signal']}*
🔥 Confidence: {decision['confidence']}
🧠 Logika: {decision['math_explanation']}

💡 *Saran Eksekusi:* {decision['trade_plan']}
"""
        send_telegram(msg)
        print(f"Sinyal {event_title} ({main_event['wib_date']}) terkirim!")
        
    # Footer info market saat ini
    market_msg = f"""
📊 *KONDISI MARKET SAAT INI (Acuan):*
- Harga Gold: ${market_context['gold_price']:.2f}
- DXY: {market_context['dxy_change_pct']}%
- Minyak: {market_context['oil_change_5d_pct']}%
"""
    send_telegram(market_msg)
    print("Semua sinyal dan konteks market terkirim!")

if __name__ == "__main__":
    run_agent()
