import requests
import os
import json
import re

def get_ai_decision(news_title, quant_context, market_context):
    api_key = os.getenv("GROQ_API_KEY")
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    prompt = f"""
    Kamu adalah Macro Quant Trader Institusi Spesialis XAUUSD.
    Hari ini ada rilis berita utama: {news_title}.
    
    [DATA KUANTITATIF UTAMA]
    - Surprise Score Utama (S_t): {quant_context['main_surprise_score']}
    
    [DASHBOARD DATA MAKRO TERBARU]
    Ini adalah data Actual dari indikator ekonomi penting yang sudah rilis (30 hari terakhir).
    {json.dumps(quant_context['supporting_analysis'], indent=2)}
    
    [KONDISI MARKET SAAT INI]
    - Perubahan DXY hari ini: {market_context['dxy_change_pct']}%
    - Perubahan Harga Minyak 5 Hari: {market_context['oil_change_5d_pct']}%
    
    [ATURAN ANALISA]
    1. FOKUS PADA ACTUAL: Jika ada data Actual, bandingkan dengan Forecast-nya. Actual > Forecast = Hawkish (SELL Gold). Actual < Forecast = Dovish (BUY Gold).
    2. CROSS-CHECK: Bagaimana kondisi inflasi (CPI/PCE) dan tenaga kerja (NFP) secara keseluruhan berdasarkan Dashboard? Apakah The Fed akan cenderung Hawkish atau Dovish minggu ini?
    3. KONTEKS MARKET: DXY naik + Minyak naik = Konfirmasi kuat bias SELL.
    4. KHUSUS FOMC: Gunakan Dashboard Makro untuk memprediksi nada bicara Powell.
    
    Tugasmu:
    Gabungkan berita utama, dashboard data makro (Actual), dan kondisi market untuk memprediksi arah XAUUSD.
    
    Output WAJIB JSON:
    {{
        "signal": "BUY / SELL / NO TRADE",
        "confidence": "High / Medium / Low",
        "math_explanation": "Jelaskan bagaimana dashboard data makro mempengaruhi prediksi",
        "trade_plan": "Aksi untuk XAUUSD"
    }}
    """
    
    models = ["openai/gpt-oss-120b", "openai/gpt-oss-20b"]
    
    for model_name in models:
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"}
        }
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=30).json()
            if "error" in resp:
                print(f"[MODEL {model_name} GAGAL] {resp['error']}")
                continue
            
            raw_content = resp["choices"][0]["message"]["content"]
            clean_json = re.sub(r'```json\n?|```', '', raw_content).strip()
            return json.loads(clean_json)
            
        except Exception as e:
            print(f"[MODEL {model_name} EXCEPTION] {e}")
            continue
    
    return {"signal": "ERROR", "math_explanation": "Semua model Groq gagal diakses.", "confidence": "-", "trade_plan": "-"}
