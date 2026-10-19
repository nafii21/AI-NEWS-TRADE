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
    
    [DATA KUANTITATIF]
    - Surprise Score Utama (S_t): {quant_context['main_surprise_score']}
    - Skor Data Pendukung: {json.dumps(quant_context['supporting_analysis'], indent=2)}
    
    [KONDISI MARKET SAAT INI]
    - Perubahan DXY hari ini: {market_context['dxy_change_pct']}%
    - Perubahan Harga Minyak 5 Hari: {market_context['oil_change_5d_pct']}%
    
    [ATURAN ANALISA DATA PENDUKUNG]
    1. DATA TENAGA KERJA (ADP, Jobless, NFP): Skor positif = Ekonomi kuat (Hawkish) -> SELL Gold. Skor negatif = Ekonomi lemah (Dovish) -> BUY Gold.
    2. DATA INFLASI (CPI, PPI, PCE): Skor positif = Inflasi panas (Hawkish) -> SELL Gold. Skor negatif = Inflasi melandai (Dovish) -> BUY Gold.
    3. UPAH (Average Hourly Earnings, Employment Cost): Skor positif = Daya beli naik, inflasi jasa panas (Hawkish) -> SELL Gold.
    4. PERMINTAAN (Retail Sales, Consumer Confidence): Skor positif = Konsumen belanja agresif (Demand-Pull Inflation) -> SELL Gold.
    5. PERTUMBUHAN (GDP): Skor positif = Ekonomi ekspansif (Hawkish) -> SELL Gold.
    6. KONTEKS MARKET: Jika DXY naik dan Minyak naik, ini konfirmasi kuat pasar lagi diskon Gold (Bearish).
    
    Tugasmu:
    Gabungkan berita utama, semua data pendukung di atas, dan kondisi market untuk memprediksi arah XAUUSD.
    
    Output WAJIB berupa JSON valid TANPA teks tambahan, TANPA markdown block:
    {{
        "signal": "BUY / SELL / NO TRADE",
        "confidence": "High / Medium / Low",
        "math_explanation": "Jelaskan korelasi angka S_t dengan data pendukung & market",
        "trade_plan": "Aksi untuk XAUUSD"
    }}
    """
    
    # Daftar model pengganti resmi dari Groq
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
            
            # Kalau model ini error, coba model berikutnya
            if "error" in resp:
                print(f"[MODEL {model_name} GAGAL] {resp['error']}")
                continue
            
            raw_content = resp["choices"][0]["message"]["content"]
            clean_json = re.sub(r'```json\n?|```', '', raw_content).strip()
            return json.loads(clean_json)
            
        except Exception as e:
            print(f"[MODEL {model_name} EXCEPTION] {e}")
            continue
    
    # Kalau semua model gagal
    return {"signal": "ERROR", "math_explanation": "Semua model Groq gagal diakses. Cek API Key atau limit.", "confidence": "-", "trade_plan": "-"}
