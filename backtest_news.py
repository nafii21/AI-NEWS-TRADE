import os
import requests
import json
from datetime import datetime, timedelta, timezone
import traceback
from quant_engine import build_pre_news_quant
from ai_decider import get_ai_decision

# ====================================================
# SKENARIO TUNGGAL: CPI 12 AGUSTUS 2026
# ====================================================
NEWS_TITLE = "CPI m/m"
FORECAST = 0.3
PREVIOUS = 0.4
NEWS_DATE_UTC = "2026-08-12 12:30:00"

SUPPORTING_DATA = {
    "Core CPI m/m": {"forecast": 0.3, "previous": 0.3},
    "PPI m/m": {"forecast": 0.2, "previous": 0.2}
}

DXY_CHANGE_PCT = -0.20 
OIL_CHANGE_PCT = -1.5  
# ====================================================

# --- KONFIGURASI TWELVE DATA ---
TWELVE_DATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY")
if not TWELVE_DATA_API_KEY:
    raise ValueError("API Key Twelve Data belum di-set. Tambahkan secret TWELVE_DATA_API_KEY di GitHub.")

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
    
    # Format tanggal untuk API (YYYY-MM-DD HH:MM:SS)
    start_date = (target_time - timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")
    end_date = (target_time + timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")
    
    url = "https://api.twelvedata.com/time_series"
    params = {
        "symbol": "XAU/USD",      # Gold Spot
        "interval": "5min",       # 5 menit
        "start_date": start_date,
        "end_date": end_date,
        "timezone": "UTC",
        "apikey": TWELVE_DATA_API_KEY,
        "order": "ASC"
    }
    
    try:
        response = requests.get(url, params=params, timeout=15).json()
        
        if response.get("status") == "error":
            print(f"[TWELVE DATA ERROR] {response.get('message')}")
            return None
            
        values = response.get("values", [])
        if not values:
            print(f"[TWELVE DATA] Data kosong untuk {start_date} - {end_date}")
            return None
            
        closest_candle = values[0]
        return float(closest_candle["close"])
        
    except Exception as e:
        print(f"[TWELVE DATA EXCEPTION] {e}")
        return None

def run_backtest():
    try:
        send_telegram(f"⏳ *Memulai Backtest (Twelve Data):* {NEWS_TITLE}...")
        
        news_dt = datetime.strptime(NEWS_DATE_UTC, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        
        # Narik data dari Twelve Data
        price_before = get_price_at_time_twelvedata(news_dt, -5)
        price_after = get_price_at_time_twelvedata(news_dt, 30)
        
        if not price_before or not price_after:
            send_telegram(f"❌ Gagal ambil data historis Gold dari Twelve Data untuk {NEWS_TITLE}.")
            return

        quant_context = build_pre_news_quant(NEWS_TITLE, FORECAST, PREVIOUS, SUPPORTING_DATA)
        market_context = {"dxy_change_pct": DXY_CHANGE_PCT, "oil_change_5d_pct": OIL_CHANGE_PCT}

        decision = get_ai_decision(NEWS_TITLE, quant_context, market_context)
        
        if not decision or decision.get('signal') == "ERROR":
            error_msg = decision.get('math_explanation', 'Unknown Error') if decision else 'Gagal API Groq'
            send_telegram(f"❌ *AI Error:*\n{error_msg}")
            return

        ai_signal = decision['signal']
        price_moved_up = price_after > price_before
        actual_direction = "BUY" if price_moved_up else "SELL"
        status_benar = "✅ BENAR" if ai_signal == actual_direction else ("🤷‍♂️ NO TRADE" if ai_signal == "NO TRADE" else "❌ SALAH")
        
        msg = f"""
🧪 *HASIL BACKTEST (TWELVE DATA)*
📅 Event: {NEWS_TITLE}

📊 *Data Gold:*
Sebelum: ${price_before:.2f}
Sesudah: ${price_after:.2f}

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
        print("Backtest Selesai!")

    except Exception as e:
        error_trace = traceback.format_exc()
        print(error_trace)
        send_telegram(f"💥 *Script Crash:*\n```\n{error_trace[-300:]}\n```")

if __name__ == "__main__":
    run_backtest()
