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
    Gunakan logika makro di bawah ini untuk menafsirkan skor data pendukung:
    1. DATA TENAGA KERJA (ADP, Jobless, NFP): Skor positif = Ekonomi kuat (Hawkish) -> SELL Gold. Skor negatif = Ekonomi lemah (Dovish) -> BUY Gold.
    2. DATA INFLASI (CPI, PPI, PCE): Skor positif = Inflasi panas (Hawkish) -> SELL Gold. Skor negatif = Inflasi melandai (Dovish) -> BUY Gold.
    3. UPAH (Average Hourly Earnings, Employment Cost): Skor positif = Daya beli naik, inflasi jasa panas (Hawkish) -> SELL Gold.
    4. PERTUMBUHAN (GDP, Retail Sales): Skor positif = Ekonomi ekspansif (Hawkish) -> SELL Gold.
    5. KEPERCAYAAN (Consumer Confidence): Skor positif = Konsumen optimis (Hawkish) -> SELL Gold.
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
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"}
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    resp = None
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=30).json()
        if "error" in resp: 
            return {"signal": "ERROR", "math_explanation": str(resp["error"]), "confidence": "-", "trade_plan": "-"}
        
        raw_content = resp["choices"][0]["message"]["content"]
        clean_json = re.sub(r'```json\n?|```', '', raw_content).strip()
        return json.loads(clean_json)
    except Exception as e:
        return {"signal": "ERROR", "math_explanation": f"Gagal parsing: {e}", "confidence": "-", "trade_plan": "-"}
