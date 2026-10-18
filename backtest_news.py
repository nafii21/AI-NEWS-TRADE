import os
import requests
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta, timezone
import traceback
from quant_engine import build_pre_news_quant
from ai_decider import get_ai_decision

# ====================================================
# DAFTAR SKENARIO BACKTEST (AGUSTUS 2026)
# ====================================================
SCENARIOS = [
    {
        "title": "Non-Farm Employment Change",
        "forecast": 175.0,
        "previous": 206.0,
        "date_utc": "2026-08-07 12:30:00", # Rilis NFP
        "supporting": {
            "ADP Non-Farm Employment Change": {"forecast": 150.0, "previous": 155.0},
            "Unemployment Rate": {"forecast": 4.1, "previous": 4.1}
        },
        "dxy_change": -0.35,
        "oil_change": 1.2
    },
    {
        "title": "CPI m/m",
        "forecast": 0.3,
        "previous": 0.4,
        "date_utc": "2026-08-12 12:30:00", # Rilis CPI
        "supporting": {
            "Core CPI m/m": {"forecast": 0.3, "previous": 0.3},
            "PPI m/m": {"forecast": 0.2, "previous": 0.2}
        },
        "dxy_change": -0.20,
        "oil_change": -1.5
    }
]
# ====================================================

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(msg):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID: return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
    except: pass

def get_price_at_time(ticker, target_dt, offset_minutes):
    start_date = (target_dt - timedelta(days=3)).strftime("%Y-%m-%d")
    end_date = (target_dt + timedelta(days=3)).strftime("%Y-%m-%d")
    
    df = yf.download(ticker, start=start_date, end=end_date, interval="5m", progress=False)
    if df.empty: return None
    
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
    send_telegram("⏳ *Memulai Backtest News (Agustus 2026): NFP & CPI*...")
    
    for scen in SCENARIOS:
        try:
            print(f"\n=== MENGUJI SKENARIO: {scen['title']} ({scen['date_utc']}) ===")
            news_dt = datetime.strptime(scen['date_utc'], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            
            price_before = get_price_at_time("GC=F", news_dt, -5)
            price_after = get_price_at_time("GC=F", news_dt, 30)
            
            if not price_before or not price_after:
                send_telegram(f"❌ Gagal ambil data historis Gold untuk {scen['title']}.")
                continue

            print(f"Harga Gold T-5m: {price_before:.2f} | T+30m: {price_after:.2f}")
            
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
🧪 *HASIL BACKTEST AGUSTUS 2026*
📅 Event: {scen['title']}

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
            print(f"Backtest {scen['title']} Selesai!")

        except Exception as e:
            error_trace = traceback.format_exc()
            print(error_trace)
            send_telegram(f"💥 *Script Crash di {scen['title']}:*\n```\n{error_trace[-300:]}\n```")

if __name__ == "__main__":
    run_backtest()
