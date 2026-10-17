import requests
import os
import json

def get_ai_decision(news_title, quant_context, dxy_change):
    api_key = os.getenv("GROQ_API_KEY")
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    prompt = f"""
    Kamu adalah Macro Quant Trader Institusi.
    Kita akan menganalisa arah XAUUSD sebelum rilis berita: {news_title}.
    
    [RUMUS MATEMATIKA QUANT - NEWS SURPRISE SCORE]
    Score Utama (Forecast vs Previous): {quant_context['main_surprise_score']}
    Skor Data Pendukung: {json.dumps(quant_context['supporting_analysis'], indent=2)}
    Konteks DXY hari ini: {dxy_change}%
    
    Tugasmu:
    1. Jika Score Utama POSITIF BESAR (> 1.0): Pasar ekspektasi data sangat bagus (Hawkish/Inflasi tinggi). USD menguat -> XAUUSD berpotensi TURUN (SELL).
    2. Jika Score Utama NEGATIF BESAR (< -1.0): Pasar ekspektasi data sangat buruk (Dovish). USD melemah -> XAUUSD berpotensi NAIK (BUY).
    3. CROSS-CHECK dengan Data Pendukung! Jika Score Utama Positif, TAPI skor ADP negatif, berarti ekspektasi bisa meleset. Waspada (NO TRADE / Low Confidence).
    
    Output WAJIB JSON:
    {{
        "signal": "BUY / SELL / NO TRADE",
        "confidence": "High / Medium / Low",
        "math_explanation": "Jelaskan logika arah harga berdasarkan rumus S_t di atas",
        "trade_plan": "Aksi untuk XAUUSD"
    }}
    """
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"}
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=30).json()
        return json.loads(resp["choices"][0]["message"]["content"])
    except Exception as e:
        print(f"AI Error: {e}")
        return None
