import os
import requests
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta, timezone
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

def get_historical_market_context():
    return {"dxy_change_pct": DXY_CHANGE_PCT, "oil_change_5d_pct": OIL_CHANGE_PCT}

def get_price_at_time(ticker, target_dt, offset_minutes):
    """Ambil harga 5 menit sebelum atau 30 menit sesudah news."""
    start_date = (target_dt - timedelta(days=3)).strftime("%Y-%m-%d")
    end_date = (target_dt + timedelta(days=3)).strftime("%Y-%m-%d")
    
    df = yf.download(ticker, start=start_date, end=end_date, interval="5m", progress=False)
    if df.empty:
        return None
    
    # --- PERBAIKAN MULTI-INDEX DARI YFINANCE ---
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    # -------------------------------------------

    target_time = target_dt + timedelta(minutes=offset_minutes)
    
    if df.index.tz is not None:
        target_time = target_time.astimezone(df.index.tz)
    else:
        target_time = target_time.replace(tzinfo=None)

    closest_idx = df.index.get_indexer([target_time], method='nearest')[0]
    
    # Pastikan ngambil nilai scalar (float)
    val = df['Close'].iloc[closest_idx]
    return float(val) if not isinstance(val, pd.Series) else float(val.iloc[0])

def run_backtest():
    print(f"=== MENGUJI SKENARIO: {NEWS_TITLE} ({NEWS_DATE_UTC} UTC) ===")
    
    news_dt = datetime.strptime(NEWS_DATE_UTC, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    
    price_before = get_price_at_time("GC=F", news_dt, -5)
    price_after = get_price_at_time("GC=F", news_dt, 30)
    
    if not price_before or not price_after:
        print("❌ Gagal ambil data historis Gold dari yfinance.")
        return

    print(f"💰 Harga Gold T-5m : ${price_before:.2f}")
    print(f"💰 Harga Gold T+30m: ${price_after:.2f}")
    
    print("\n⏳ Menghitung Surprise Score (Quant Engine)...")
    quant_context = build_pre_news_quant(NEWS_TITLE, FORECAST, PREVIOUS, SUPPORTING_DATA)
    
    print(f"🧮 Main Surprise Score (S_t): {quant_context['main_surprise_score']}")
    print("📉 Supporting Data Score:")
    for k, v in quant_context['supporting_analysis'].items():
        print(f"   - {k}: {v}")

    print("\n⏳ Mengambil Data DXY & Minyak Historis...")
    market_context = get_historical_market_context()
    print(f"🌍 DXY Change: {market_context['dxy_change_pct']}%")
    print(f"🌍 Oil 5D Change: {market_context['oil_change_5d_pct']}%")

    print("\n🧠 Meminta AI mengambil keputusan...")
    decision = get_ai_decision(NEWS_TITLE, quant_context, market_context)
    
    if not decision:
        print("❌ AI gagal kasih sinyal.")
        return

    ai_signal = decision['signal']
    print(f"\n🎯 SINYAL AI: {ai_signal} (Confidence: {decision['confidence']})")
    print(f"💡 Alasan AI: {decision['math_explanation']}")
    print(f"📋 Saran Eksekusi: {decision['trade_plan']}")
    
    price_moved_up = price_after > price_before
    actual_direction = "BUY" if price_moved_up else "SELL"
    
    print(f"\n📊 REALITA MARKET: Gold {'NAIK' if price_moved_up else 'TURUN'} (Arah: {actual_direction})")
    
    if ai_signal == "NO TRADE":
        print("🤷‍♂️ HASIL: AI memilih NO TRADE (Aman, tidak dievaluasi).")
    elif ai_signal == actual_direction:
        print("✅ HASIL: PREDIKSI AI BENAR! 🔥")
    else:
        print("❌ HASIL: PREDIKSI AI SALAH (Fakeout / Kebalik).")

if __name__ == "__main__":
    run_backtest()
