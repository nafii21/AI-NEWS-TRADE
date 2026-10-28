import requests
import os
import json
import re

def get_ai_decision(news_title, quant_context, market_context):
    api_key = os.getenv("SAKELAR_API_KEY")
    url = "https://api.sakelar.web.id/v1/chat/completions"
    model_name = "deepseek-v4.1-flash"
    
    prompt = f"""
    Kamu adalah Macro Quant Trader Institusi Spesialis XAUUSD (Gold).
    Hari ini ada rilis berita utama: {news_title}.
    
    [DATA KUANTITATIF]
    - Surprise Score Utama (S_t): {quant_context['main_surprise_score']}
    - Skor Data Pendukung: {json.dumps(quant_context['supporting_analysis'], indent=2)}
    
    [KONDISI MARKET SAAT INI]
    - Perubahan DXY hari ini: {market_context['dxy_change_pct']}%
    - Perubahan Harga Minyak: {market_context['oil_change_5d_pct']}%
    
    [SOP PRIORITAS ANALISA - WAJIB DIPATUHI]
    1. DILARANG KERAS memilih "NO TRADE" kecuali semua data benar-benar 0.0 (tidak ada data). Kamu HARUS memilih BUY atau SELL.
    2. Jika data campur aduk (ada Hawkish dan Dovish), IKUTI PRIORITAS THE FED: 
       - Inflasi (CPI, PPI, Core PCE) adalah RAJA. Jika inflasi panas (Skor Positif > 0.5), abaikan data tenaga kerja yang lemah, kamu WAJIB pilih SELL.
       - Jika Inflasi dingin (Skor Negatif < -0.5), abaikan data tenaga kerja yang kuat, kamu WAJIB pilih BUY.
    3. Data Tenaga Kerja (NFP, ADP, AHE) hanya dipakai sebagai penentu arah jika data Inflasi netral atau tidak ada.
    4. KONTEKS MARKET: DXY naik = konfirmasi SELL. DXY turun = konfirmasi BUY. Minyak naik = inflasi naik = SELL.
    
    Tugasmu:
    Tentukan arah XAUUSD dengan tegas (BUY/SELL) berdasarkan SOP Prioritas di atas.
    
    ATURAN BAHASA:
    Gunakan BAHASA INDONESIA yang baku dan profesional.
    
    Output WAJIB JSON:
    {{
        "signal": "BUY / SELL",
        "confidence": "High / Medium / Low",
        "math_explanation": "Jelaskan analisa kamu berdasarkan SOP Prioritas (misal: Inflasi panas, maka SELL)",
        "trade_plan": "Saran eksekusi trading untuk XAUUSD (Bahasa Indonesia)"
    }}
    """
    
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": "Kamu adalah analis makro profesional yang tegas dan hanya membalas dengan JSON valid."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "response_format": {"type": "json_object"}
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=45)
        resp = response.json()
        
        if "error" in resp:
            print(f"[SAKELAR ERROR] {resp['error']}")
            return {"signal": "ERROR", "math_explanation": str(resp["error"]), "confidence": "-", "trade_plan": "-"}
            
        raw_content = resp["choices"][0]["message"]["content"]
        clean_json = re.sub(r'```json\n?|```', '', raw_content).strip()
        return json.loads(clean_json)
        
    except Exception as e:
        print(f"[SAKELAR EXCEPTION] {e}")
        return {"signal": "ERROR", "math_explanation": f"Gagal parsing: {e}", "confidence": "-", "trade_plan": "-"}
