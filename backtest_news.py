import os
import requests
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta, timezone
import traceback
from quant_engine import build_pre_news_quant
from ai_decider import get_ai_decision

# ====================================================
# INPUT SKENARIO HISTORIS (CPI 14 OKTOBER 2026)
# ====================================================
NEWS_TITLE = "CPI m/m"
FORECAST = 0.6
PREVIOUS = 0.4
NEWS_DATE_UTC = "2026-10-14 12:30:00" 

SUPPORTING_DATA = {
    "PPI m/m": {"forecast": 0.6, "previous": 0.4},
    "Core CPI m/m": {"forecast": 0.2, "previous": 0.3}
}

DXY_CHANGE_PCT = 0.35
OIL_CHANGE_PCT = 5.0
# ====================================================

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(msg):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
    except:
        pass

def get_historical_market_context():
    return {"dxy_change_pct": DXY_CHANGE_PCT, "oil_change_5d_pct": OIL_CHANGE_PCT}

def get_price_at_time(ticker, target_dt, offset_minutes):
    start_date = (target_dt - timedelta(days=3)).strftime("%Y-%m-%d")
    end_date = (target_dt + timedelta(days=3)).strftime("%Y-%m-%d")
    
    df = yf.download(ticker, start=start_date, end=end_date, interval="5m", progress=False)
    if df.empty:
        return None
    
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    target_time = target_dt + timedelta(minutes=offset_minutes)
    
    if df.index.tz is not None:
        target_time = target_time.astimezone(df.index.tz)
    else:
        target_time = target_time.replace(tzinfo=None)

    closest_idx = df.index.get_indexer([target_time], method='nearest')[0]
    val = df['Close'].iloc[closest_idx]
    return float(val) if not isinstance(val, pd.Series) else float(val.iloc[0])

def run_backtest():
    try:
        print(f"=== MENGUJI SKENARIO: {NEWS_TITLE} ({NEWS_DATE_UTC} UTC) ===")
        send_telegram(f"⏳ *Memulai Backtest:* {NEWS_TITLE}...\n_(Sedang menarik data, mohon tunggu 15-30 detik)_")
        
        news_dt = datetime.strptime(NEWS_DATE_UTC, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        
        print("Menarik data harga Gold...")
        price_before = get_price_at_time("GC=F", news_dt, -5)
        price_after = get_price_at_time("GC=F", news_dt, 30)
        
        if not price_before or not price_after:
            send_telegram("❌ Gagal ambil data historis Gold dari yfinance (Data kosong).")
            return

        print(f"Harga Gold T-5m: {price_before:.2f} | T+30m: {price_after:.2f}")
        
        print("Menghitung Surprise Score...")
        quant_context = build_pre_news_quant(NEWS_TITLE, FORECAST, PREVIOUS, SUPPORTING_DATA)
        
        market_context = get_historical_market_context()

        print("Meminta AI mengambil keputusan...")
        decision = get_ai_decision(NEWS_TITLE, quant_context, market_context)
        
        if not decision or decision.get('signal') == "ERROR":
            error_msg = decision.get('math_explanation', 'Unknown Error') if decision else 'Gagal nembak API Groq'
            send_telegram(f"❌ *AI Error:*\n{error_msg}")
            return

        ai_signal = decision['signal']
        price_moved_up = price_after > price_before
        actual_direction = "BUY" if price_moved_up else "SELL"
        status_benar = "✅ BENAR" if ai_signal == actual_direction else ("🤷‍♂️ NO TRADE" if ai_signal == "NO TRADE" else "❌ SALAH")
        
        msg = f"""
🧪 *HASIL BACKTEST NEWS*
📅 Event: {NEWS_TITLE}

📊 *Data Gold:*
T-5 Menit : ${price_before:.2f}
T+30 Menit: ${price_after:.2f}

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
        send_telegram(f"💥 *Script Crash:*\n```\n{error_trace[-400:]}\n```")

if __name__ == "__main__":
    run_backtest()
