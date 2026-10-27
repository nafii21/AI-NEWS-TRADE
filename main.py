import os
import requests
import time
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
        resp = requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
        if resp.status_code != 200:
            requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg}, timeout=10)
    except Exception as e:
        print(f"Error Telegram: {e}")

def run_agent():
    print("Memulai Analisa Live (Proyeksi 3 Hari)...")
    processed_events = get_news_and_cluster()
    
    today_date = datetime.now().strftime("%Y-%m-%d")
    
    if not processed_events:
        print("Tidak ada berita High Impact USD untuk 3 hari ke depan.")
        send_telegram(f"🔍 *Hasil Pengecekan ({today_date}):*\nTidak ada berita High Impact USD untuk 3 hari ke depan. Bot standby.")
        return

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
        
        # Format skor pendukung
        support_text = ""
        if quant_context['supporting_analysis']:
            for k, v in quant_context['supporting_analysis'].items():
                tgl = v.get('date', 'Tgl ?')
                support_text += f"  - {k} ({tgl}): {v['desc']} (Skor: {v['score']})\n"
        else:
            support_text = "  - Tidak ada data pendukung\n"

        msg = f"""
🌍 *PREDIKSI MACRO QUANT (LIVE)*
📆 Tanggal Rilis: {main_event['wib_date']}
📅 Event: {event_title}
⏰ Jam: {main_event['wib_time']} WIB
📊 Forecast: {main_event['forecast']} | Prev: {main_event['previous']}

🧮 *Skor Kejutan (S_t): {quant_context['main_surprise_score']}*
📉 *Data Makro Pendukung:*
{support_text}
🌍 *Kondisi Market Saat Ini:*
- Harga Gold: ${market_context['gold_price']:.2f}
- DXY: {market_context['dxy_change_pct']}%
- Minyak: {market_context['oil_change_5d_pct']}%

🎯 *PREDIKSI AI: {decision['signal']}*
🔥 Tingkat Keyakinan: {decision['confidence']}
🧠 Alasan Logis: {decision['math_explanation']}

💡 *Saran Eksekusi:* {decision['trade_plan']}
"""
        send_telegram(msg)
        print(f"Sinyal {event_title} ({main_event['wib_date']}) terkirim!")
        
        time.sleep(3)
        
    market_msg = f"""
📊 *KONDISI MARKET (Acuan Akhir):*
- Harga Gold: ${market_context['gold_price']:.2f}
- DXY: {market_context['dxy_change_pct']}%
- Minyak: {market_context['oil_change_5d_pct']}%
"""
    send_telegram(market_msg)
    print("Semua sinyal dan konteks market terkirim!")

if __name__ == "__main__":
    run_agent()
