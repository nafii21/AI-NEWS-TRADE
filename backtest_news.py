import os
import requests
import json
import time
from datetime import datetime, timedelta, timezone
import traceback
from quant_engine import build_pre_news_quant
from ai_decider import get_ai_decision

# ====================================================
# KUMPULAN SKENARIO BACKTEST 2026 (CPI, NFP, PCE, RETAIL)
# ====================================================
SCENARIOS = [
    # --- JANUARI 2026 ---
    {"title": "CPI m/m", "forecast": 2.7, "previous": 2.7, "date_utc": "2026-01-13 13:30:00", "supporting": {"Core CPI m/m": {"forecast": 3.1, "previous": 3.0}}, "dxy_change": 0.0, "oil_change": 0.0},
    {"title": "NFP (Non-Farm Payrolls)", "forecast": 60.0, "previous": 56.0, "date_utc": "2026-01-09 13:30:00", "supporting": {"ADP Non-Farm Employment Change": {"forecast": 50.0, "previous": 40.0}}, "dxy_change": 0.0, "oil_change": 0.0},
    {"title": "Core PCE Price Index m/m", "forecast": 2.8, "previous": 2.7, "date_utc": "2026-01-22 13:30:00", "supporting": {"PCE Price Index m/m": {"forecast": 2.9, "previous": 2.8}}, "dxy_change": 0.0, "oil_change": 0.0},
    {"title": "Retail Sales m/m", "forecast": 0.5, "previous": -0.1, "date_utc": "2026-01-14 13:30:00", "supporting": {"Core Retail Sales m/m": {"forecast": 0.4, "previous": -0.1}}, "dxy_change": 0.0, "oil_change": 0.0},

    # --- FEBRUARI 2026 ---
    {"title": "CPI m/m", "forecast": 2.5, "previous": 2.7, "date_utc": "2026-02-13 13:30:00", "supporting": {"Core CPI m/m": {"forecast": 3.0, "previous": 3.1}}, "dxy_change": 0.0, "oil_change": 0.0},
    {"title": "NFP (Non-Farm Payrolls)", "forecast": 66.0, "previous": 48.0, "date_utc": "2026-02-11 13:30:00", "supporting": {"ADP Non-Farm Employment Change": {"forecast": 60.0, "previous": 50.0}}, "dxy_change": 0.0, "oil_change": 0.0},
    {"title": "Core PCE Price Index m/m", "forecast": 2.9, "previous": 2.8, "date_utc": "2026-02-20 13:30:00", "supporting": {"PCE Price Index m/m": {"forecast": 3.0, "previous": 2.9}}, "dxy_change": 0.0, "oil_change": 0.0},
    {"title": "Retail Sales m/m", "forecast": 0.4, "previous": 0.6, "date_utc": "2026-02-10 13:30:00", "supporting": {"Core Retail Sales m/m": {"forecast": 0.3, "previous": 0.5}}, "dxy_change": 0.0, "oil_change": 0.0},

    # --- MARET 2026 ---
    {"title": "CPI m/m", "forecast": 2.4, "previous": 2.4, "date_utc": "2026-03-11 13:30:00", "supporting": {"Core CPI m/m": {"forecast": 2.9, "previous": 3.0}}, "dxy_change": 0.0, "oil_change": 0.0},
    {"title": "NFP (Non-Farm Payrolls)", "forecast": 58.0, "previous": 126.0, "date_utc": "2026-03-06 13:30:00", "supporting": {"ADP Non-Farm Employment Change": {"forecast": 55.0, "previous": 60.0}}, "dxy_change": 0.0, "oil_change": 0.0},
    {"title": "Core PCE Price Index m/m", "forecast": 3.1, "previous": 3.0, "date_utc": "2026-03-13 13:30:00", "supporting": {"PCE Price Index m/m": {"forecast": 3.2, "previous": 3.0}}, "dxy_change": 0.0, "oil_change": 0.0},
    {"title": "Retail Sales m/m", "forecast": -0.3, "previous": 0.0, "date_utc": "2026-03-06 13:30:00", "supporting": {"Core Retail Sales m/m": {"forecast": -0.2, "previous": 0.1}}, "dxy_change": 0.0, "oil_change": 0.0},

    # --- APRIL 2026 ---
    {"title": "CPI m/m", "forecast": 3.4, "previous": 2.4, "date_utc": "2026-04-10 12:30:00", "supporting": {"Core CPI m/m": {"forecast": 3.2, "previous": 2.9}}, "dxy_change": 0.0, "oil_change": 0.0},
    {"title": "NFP (Non-Farm Payrolls)", "forecast": 65.0, "previous": -133.0, "date_utc": "2026-04-03 12:30:00", "supporting": {"ADP Non-Farm Employment Change": {"forecast": 60.0, "previous": 55.0}}, "dxy_change": 0.0, "oil_change": 0.0},
    {"title": "Core PCE Price Index m/m", "forecast": 3.0, "previous": 3.1, "date_utc": "2026-04-09 12:30:00", "supporting": {"PCE Price Index m/m": {"forecast": 3.1, "previous": 3.2}}, "dxy_change": 0.0, "oil_change": 0.0},
    {"title": "Retail Sales m/m", "forecast": 0.5, "previous": -0.1, "date_utc": "2026-04-01 12:30:00", "supporting": {"Core Retail Sales m/m": {"forecast": 0.4, "previous": -0.2}}, "dxy_change": 0.0, "oil_change": 0.0},

    # --- MEI 2026 ---
    {"title": "CPI m/m", "forecast": 3.7, "previous": 3.3, "date_utc": "2026-05-12 12:30:00", "supporting": {"Core CPI m/m": {"forecast": 3.4, "previous": 3.2}}, "dxy_change": 0.0, "oil_change": 0.0},
    {"title": "NFP (Non-Farm Payrolls)", "forecast": 65.0, "previous": 185.0, "date_utc": "2026-05-08 12:30:00", "supporting": {"ADP Non-Farm Employment Change": {"forecast": 70.0, "previous": 60.0}}, "dxy_change": 0.0, "oil_change": 0.0},
    {"title": "Core PCE Price Index m/m", "forecast": 3.2, "previous": 3.0, "date_utc": "2026-04-30 12:30:00", "supporting": {"PCE Price Index m/m": {"forecast": 3.3, "previous": 3.1}}, "dxy_change": 0.0, "oil_change": 0.0},
    {"title": "Retail Sales m/m", "forecast": 0.5, "previous": 1.7, "date_utc": "2026-05-14 12:30:00", "supporting": {"Core Retail Sales m/m": {"forecast": 0.4, "previous": 1.5}}, "dxy_change": 0.0, "oil_change": 0.0},

    # --- JUNI 2026 ---
    {"title": "CPI m/m", "forecast": 4.2, "previous": 3.8, "date_utc": "2026-06-10 12:30:00", "supporting": {"Core CPI m/m": {"forecast": 3.8, "previous": 3.4}}, "dxy_change": 0.0, "oil_change": 0.0},
    {"title": "NFP (Non-Farm Payrolls)", "forecast": 85.0, "previous": 179.0, "date_utc": "2026-06-05 12:30:00", "supporting": {"ADP Non-Farm Employment Change": {"forecast": 80.0, "previous": 70.0}}, "dxy_change": 0.0, "oil_change": 0.0},
    {"title": "Core PCE Price Index m/m", "forecast": 3.3, "previous": 3.2, "date_utc": "2026-05-28 12:30:00", "supporting": {"PCE Price Index m/m": {"forecast": 3.4, "previous": 3.3}}, "dxy_change": 0.0, "oil_change": 0.0},
    {"title": "Retail Sales m/m", "forecast": 0.5, "previous": 0.9, "date_utc": "2026-06-17 12:30:00", "supporting": {"Core Retail Sales m/m": {"forecast": 0.4, "previous": 0.8}}, "dxy_change": 0.0, "oil_change": 0.0},

    # --- JULI 2026 ---
    {"title": "CPI m/m", "forecast": 3.8, "previous": 4.2, "date_utc": "2026-07-14 12:30:00", "supporting": {"Core CPI m/m": {"forecast": 3.5, "previous": 3.8}}, "dxy_change": 0.0, "oil_change": 0.0},
    {"title": "NFP (Non-Farm Payrolls)", "forecast": 114.0, "previous": 129.0, "date_utc": "2026-07-02 12:30:00", "supporting": {"ADP Non-Farm Employment Change": {"forecast": 100.0, "previous": 90.0}}, "dxy_change": 0.0, "oil_change": 0.0},
    {"title": "Core PCE Price Index m/m", "forecast": 3.4, "previous": 3.3, "date_utc": "2026-06-25 12:30:00", "supporting": {"PCE Price Index m/m": {"forecast": 3.5, "previous": 3.4}}, "dxy_change": 0.0, "oil_change": 0.0},
    {"title": "Retail Sales m/m", "forecast": 0.2, "previous": 0.9, "date_utc": "2026-07-16 12:30:00", "supporting": {"Core Retail Sales m/m": {"forecast": 0.1, "previous": 0.8}}, "dxy_change": 0.0, "oil_change": 0.0},

    # --- AGUSTUS 2026 ---
    {"title": "CPI m/m", "forecast": 3.4, "previous": 3.5, "date_utc": "2026-08-12 12:30:00", "supporting": {"Core CPI m/m": {"forecast": 3.2, "previous": 3.5}}, "dxy_change": 0.0, "oil_change": 0.0},
    {"title": "NFP (Non-Farm Payrolls)", "forecast": 85.0, "previous": 20.0, "date_utc": "2026-08-07 12:30:00", "supporting": {"ADP Non-Farm Employment Change": {"forecast": 70.0, "previous": 60.0}}, "dxy_change": 0.0, "oil_change": 0.0},
    {"title": "Core PCE Price Index m/m", "forecast": 3.3, "previous": 3.3, "date_utc": "2026-08-26 12:30:00", "supporting": {"PCE Price Index m/m": {"forecast": 3.4, "previous": 3.3}}, "dxy_change": 0.0, "oil_change": 0.0},
    {"title": "Retail Sales m/m", "forecast": 0.1, "previous": 0.2, "date_utc": "2026-08-14 12:30:00", "supporting": {"Core Retail Sales m/m": {"forecast": 0.2, "previous": 0.1}}, "dxy_change": 0.0, "oil_change": 0.0},

    # --- SEPTEMBER 2026 ---
    {"title": "CPI m/m", "forecast": 3.4, "previous": 3.4, "date_utc": "2026-09-11 12:30:00", "supporting": {"Core CPI m/m": {"forecast": 3.2, "previous": 3.2}}, "dxy_change": 0.0, "oil_change": 0.0},
    {"title": "NFP (Non-Farm Payrolls)", "forecast": 55.0, "previous": 21.0, "date_utc": "2026-09-04 12:30:00", "supporting": {"ADP Non-Farm Employment Change": {"forecast": 50.0, "previous": 40.0}}, "dxy_change": 0.0, "oil_change": 0.0},
    {"title": "Core PCE Price Index m/m", "forecast": 3.3, "previous": 3.3, "date_utc": "2026-09-30 12:30:00", "supporting": {"PCE Price Index m/m": {"forecast": 3.3, "previous": 3.4}}, "dxy_change": 0.0, "oil_change": 0.0},
    {"title": "Retail Sales m/m", "forecast": 0.8, "previous": -0.6, "date_utc": "2026-09-16 12:30:00", "supporting": {"Core Retail Sales m/m": {"forecast": 0.6, "previous": -0.5}}, "dxy_change": 0.0, "oil_change": 0.0},

    # --- OKTOBER 2026 ---
    {"title": "CPI m/m", "forecast": 3.6, "previous": 3.4, "date_utc": "2026-10-14 12:30:00", "supporting": {"Core CPI m/m": {"forecast": 3.3, "previous": 3.2}}, "dxy_change": 0.0, "oil_change": 0.0},
    {"title": "NFP (Non-Farm Payrolls)", "forecast": 89.0, "previous": 133.0, "date_utc": "2026-10-02 12:30:00", "supporting": {"ADP Non-Farm Employment Change": {"forecast": 80.0, "previous": 70.0}}, "dxy_change": 0.0, "oil_change": 0.0},
    {"title": "Core PCE Price Index m/m", "forecast": 3.3, "previous": 3.0, "date_utc": "2026-10-30 12:30:00", "supporting": {"PCE Price Index m/m": {"forecast": 3.4, "previous": 3.0}}, "dxy_change": 0.0, "oil_change": 0.0},
    {"title": "Retail Sales m/m", "forecast": 0.3, "previous": 1.2, "date_utc": "2026-10-15 12:30:00", "supporting": {"Core Retail Sales m/m": {"forecast": 0.2, "previous": 1.0}}, "dxy_change": 0.0, "oil_change": 0.0}
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
    start_date = target_time.strftime("%Y-%m-%d %H:%M:00")
    end_date = (target_time + timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M:00")
    
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
    send_telegram(f"⏳ *Memulai Backtest Masal 2026 ({len(SCENARIOS)} Skenario)*...\n_Proses ini akan memakan waktu 10-15 menit karena ada jeda API._")
    
    success_count = 0
    correct_count = 0
    total_evaluated = 0
    
    for i, scen in enumerate(SCENARIOS, 1):
        try:
            print(f"\n=== [{i}/{len(SCENARIOS)}] MENGUJI: {scen['title']} ({scen['date_utc']}) ===")
            news_dt = datetime.strptime(scen['date_utc'], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            
            price_before = get_price_at_time_twelvedata(news_dt, -5)
            time.sleep(8) # Jeda anti-limit
            price_after = get_price_at_time_twelvedata(news_dt, 5)
            time.sleep(8)
            
            if not price_before or not price_after:
                print(f"[SKIP] Gagal ambil harga untuk {scen['title']}")
                continue

            quant_context = build_pre_news_quant(scen['title'], scen['forecast'], scen['previous'], scen['supporting'])
            market_context = {"dxy_change_pct": scen['dxy_change'], "oil_change_5d_pct": scen['oil_change']}

            decision = get_ai_decision(scen['title'], quant_context, market_context)
            
            if not decision or decision.get('signal') == "ERROR":
                error_msg = decision.get('math_explanation', 'Unknown Error') if decision else 'Gagal API'
                print(f"[SKIP] AI Error: {error_msg}")
                continue

            success_count += 1
            ai_signal = decision['signal']
            price_moved_up = price_after > price_before
            actual_direction = "BUY" if price_moved_up else "SELL"
            
            status_benar = "NO EVAL"
            if ai_signal != "NO TRADE":
                total_evaluated += 1
                if ai_signal == actual_direction:
                    status_benar = "✅ BENAR"
                    correct_count += 1
                else:
                    status_benar = "❌ SALAH"
            
            tanggal_rilis = scen['date_utc'][:10]
            
            # Kirim hasil ke Telegram
            msg = f"""
🧪 *HASIL BACKTEST ({i}/{len(SCENARIOS)})*
📅 Event: {scen['title']}
📆 Tanggal: {tanggal_rilis}

📊 *Data XAUUSD:*
T-5: ${price_before:.2f} | T+5: ${price_after:.2f}

🎯 *Prediksi AI:* {ai_signal}
🔥 Confidence: {decision['confidence']}

📈 *Realita:* Gold {('NAIK' if price_moved_up else 'TURUN')}
🏁 *Hasil:* {status_benar}
"""
            send_telegram(msg)
            print(f"[DONE] {scen['title']} - {status_benar}")

        except Exception as e:
            print(f"[ERROR] {scen['title']}: {e}")

    # Rekap Akhir
    if total_evaluated > 0:
        win_rate = (correct_count / total_evaluated) * 100
        summary = f"""
🏁 *REKAP BACKTEST SELESAI*
Total Skenario: {len(SCENARIOS)}
Berhasil Dianalisa: {success_count}
Trade Dievaluasi (BUY/SELL): {total_evaluated}
Prediksi Benar: {correct_count}

🎯 *Win Rate AI: {win_rate:.1f}%*
"""
        send_telegram(summary)
    else:
        send_telegram("❌ Semua skenario gagal dievaluasi.")

if __name__ == "__main__":
    run_backtest()
