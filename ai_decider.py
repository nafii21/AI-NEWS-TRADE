import requests
import os
import json
import re

def get_ai_decision(news_title, quant_context, market_context):
    api_key = os.getenv("GROQ_API_KEY")
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    prompt = f"""
    Kamu adalah Macro Quant Trader Institusi Spesialis XAUUSD (Gold).
    Hari ini ada rilis berita utama: {news_title}.
    
    [DATA KUANTITATIF]
    - Surprise Score Utama (S_t): {quant_context['main_surprise_score']}
    - Skor Data Pendukung: {json.dumps(quant_context['supporting_analysis'], indent=2)}
    
    [KONDISI MARKET SAAT INI]
    - Perubahan DXY hari ini: {market_context['dxy_change_pct']}%
    - Perubahan Harga Minyak: {market_context['oil_change_5d_pct']}%
    
    [ATURAN ANALISA DATA]
    1. DATA INFLASI (CPI, PPI, PCE): Jika Actual > Forecast, inflasi panas (Hawkish) -> SELL Gold. Jika Actual < Forecast, inflasi melandai (Dovish) -> BUY Gold.
    2. DATA TENAGA KERJA (NFP, ADP, Unemployment): Jika Actual > Forecast, ekonomi kuat (Hawkish) -> SELL Gold.
    3. KONTEKS MARKET: Jika DXY naik dan Minyak naik, ini konfirmasi kuat pasar lagi diskon Gold (Bearish).
    4. KHUSUS FOMC: Fokus pada cross-check data Inflasi dan Tenaga Kerja terbaru. Tentukan apakah The Fed akan Hawkish atau Dovish.
    
    Tugasmu:
    Gabungkan berita utama, dashboard data makro, dan kondisi market untuk memprediksi arah XAUUSD.
    
    ATURAN BAHASA (WAJIB):
    - Gunakan BAHASA INDONESIA yang baku, profesional, dan mudah dipahami.
    - Field "math_explanation" dan "trade_plan" WAJIB menggunakan Bahasa Indonesia.
    - Jelaskan korelasi angka S_t dan data Actual vs Forecast secara logis.
    
    Output WAJIB berupa JSON valid TANPA teks tambahan, TANPA markdown block:
    {{
        "signal": "BUY / SELL / NO TRADE",
        "confidence": "High / Medium / Low",
        "math_explanation": "Jelaskan analisa makro dan korelasi datanya di sini (Bahasa Indonesia)",
        "trade_plan": "Saran eksekusi trading untuk XAUUSD (Bahasa Indonesia)"
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
