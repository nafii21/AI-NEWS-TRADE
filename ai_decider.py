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
    
    [ATURAN ANALISA]
    1. NFP: Cross-check dengan ADP/Jobless Claims. Jika NFP ekspektasi tinggi tapi ADP rendah, bisa jadi NFP meleset (Dovish -> BUY Gold).
    2. CPI: Cross-check dengan harga minyak (oil). Jika minyak naik 5 hari terakhir, ekspektasi inflasi (CPI) naik -> Hawkish (USD Kuat) -> SELL Gold.
    3. FOMC: Jika data pendukung (GDP/NFP) kuat, Fed cenderung Hawkish -> SELL Gold. Jika data campur aduk, NO TRADE.
    4. DXY: Jika DXY sedang naik kuat, ini konfirmasi USD kuat -> Tekanan ke Gold.
    
    Tugasmu:
    Gabungkan semua data di atas untuk memprediksi arah XAUUSD.
    
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
        raw_content = resp["choices"][0]["message"]["content"]
        clean_json = re.sub(r'```json\n?|```', '', raw_content).strip()
        return json.loads(clean_json)
    except Exception as e:
        print(f"RAW AI RESPONSE: {resp}")
        print(f"AI Error Asli: {e}")
        return None
