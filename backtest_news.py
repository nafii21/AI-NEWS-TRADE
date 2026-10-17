import os
import requests
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from quant_engine import build_pre_news_quant
from ai_decider import get_ai_decision

# ====== INPUT SKENARIO HISTORIS ======
NEWS_TITLE = "CPI m/m"
FORECAST = 0.3
PREVIOUS = 0.2
NEWS_DATE_UTC = "2024-01-11 13:30:00" # Waktu rilis CPI (UTC)
SUPPORTING_DATA = {} # Kosongin dulu buat tes simpel
DXY_CHANGE_PCT = 0.15 # Asumsi DXY saat itu
OIL_CHANGE_PCT = 2.5  # Asumsi Minyak saat itu

def get_price_at_time(ticker, target_dt, offset_minutes):
    """Ambil harga 5 menit sebelum atau 30 menit sesudah news."""
    start_date = (target_dt - timedelta(days=2)).strftime("%Y-%m-%d")
    end_date = (target_dt + timedelta(days=2)).strftime("%Y-%m-%d")
    
    df = yf.download(ticker, start=start_date, end=end_date, interval="1m", progress=False)
    if df.empty:
        return None
    
    target_time = target_dt + timedelta(minutes=offset_minutes)
    # Cari candle terdekat dengan target_time
    closest_idx = df.index.get_indexer([target_time], method='nearest')[0]
    return float(df['Close'].iloc[closest_idx])

def run_backtest():
    print(f"Menguji Skenario: {NEWS_TITLE} pada {NEWS_DATE_UTC} UTC...")
    
    news_dt = datetime.strptime(NEWS_DATE_UTC, "%Y-%m-%d %H:%M:%S")
    
    # 1. Ambil Harga Emas (XAUUSD proxy: GC=F) SEBELUM news (T-5 menit)
    price_before = get_price_at_time("GC=F", news_dt, -5)
    # 2. Ambil Harga Emas SESUDAH news (T+30 menit)
    price_after = get_price_at_time("GC=F", news_dt, 30)
    
    if not price_before or not price_after:
        print("Gagal ambil data historis yfinance (mungkin weekend/data kosong).")
        return

    print(f"Harga Gold T-5m: ${price_before:.2f}")
    print(f"Harga Gold T+30m: ${price_after:.2f}")
    
    # 3. Hitung Quant
    quant_context = build_pre_news_quant(NEWS_TITLE, FORECAST, PREVIOUS, SUPPORTING_DATA)
    
    # 4. Minta AI Prediksi
    market_context = {"dxy_change_pct": DXY_CHANGE_PCT, "oil_change_5d_pct": OIL_CHANGE_PCT}
    decision = get_ai_decision(NEWS_TITLE, quant_context, market_context)
    
    if not decision:
        print("AI gagal kasih sinyal.")
        return

    ai_signal = decision['signal']
    print(f"\n=== HASIL PREDIKSI AI ===")
    print(f"Sinyal AI: {ai_signal} (Confidence: {decision['confidence']})")
    print(f"Alasan AI: {decision['math_explanation']}")
    
    # 5. Evaluasi Benar / Salah
    price_moved_up = price_after > price_before
    actual_direction = "BUY" if price_moved_up else "SELL"
    
    print(f"\n=== REALITA MARKET ===")
    print(f"Arah Asli Gold: {actual_direction} (Bergerak {'NAIK' if price_moved_up else 'TURUN'})")
    
    if ai_signal == "NO TRADE":
        print("Hasil: AI memilih NO TRADE (Aman, tidak dievaluasi).")
    elif ai_signal == actual_direction:
        print("✅ HASIL: PREDIKSI AI BENAR!")
    else:
        print("❌ HASIL: PREDIKSI AI SALAH (Fakeout / Kebalik).")

if __name__ == "__main__":
    run_backtest()
