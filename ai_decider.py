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
    
    [1. BERITA UTAMA (TARGET PREDIKSI)]
    - Event: {news_title}
    - Forecast: {quant_context.get('main_forecast', 0.0)}
    - Previous: {quant_context.get('main_previous', 0.0)}
    - Skor Kejutan (S_t): {quant_context['main_surprise_score']}
    
    [2. DATA KUANTITATIF PENDUKUNG (KONTEKS HISTORIS)]
    {json.dumps(quant_context['supporting_analysis'], indent=2)}
    
    [3. KONDISI MARKET SAAT INI]
    - Perubahan DXY hari ini: {market_context['dxy_change_pct']}%
    - Perubahan Harga Minyak: {market_context['oil_change_5d_pct']}%
    
    [SOP ANALISA - WAJIB DIPATUHI]
    1. DILARANG KERAS memilih "NO TRADE". Kamu HARUS memilih BUY atau SELL.
    2. CATATAN PENTING: Data NFP historis sengaja tidak dimasukkan karena sudah *priced in*. Fokus analisa kamu adalah membandingkan *Forecast* NFP besok dengan data *Leading Indicator* (ADP, ISM, JOLTs, Challenger, dll).
    3. ATURAN FILTER DOMAIN (SANGAT PENTING):
       - JIKA BERITA UTAMA ADALAH NFP (Tenaga Kerja): ABAIKAN total data Inflasi (CPI/PPI). Fokus 100% pada data Tenaga Kerja.
       - JIKA BERITA UTAMA ADALAH CPI (Inflasi): ABAIKAN total data Tenaga Kerja. Fokus 100% pada data Inflasi.
       - JIKA BERITA UTAMA ADALAH FOMC: Gunakan data Inflasi sebagai prioritas, lalu Tenaga Kerja sebagai konfirmasi.
    4. JANGAN MENJUMLAHKAN ATAU MERATA-RATA SKOR. Nilai data mana yang paling dominan untuk memprediksi apakah NFP besok akan mencapai {quant_context.get('main_forecast', 0.0)} atau tidak.
    5. KONTEKS MARKET: DXY naik = konfirmasi SELL. DXY turun = konfirmasi BUY. Minyak naik = Inflasi naik = SELL.
    6. CONFIDENCE: Berikan "High" HANYA JIKA semua data pendukung searah. Jika campur aduk (misal ADP kuat tapi ISM lemah), WAJIB berikan "Medium".
    
    Tugasmu:
    Tentukan arah XAUUSD dengan tegas (BUY/SELL) berdasarkan prediksi NFP besok dari data pendukung di atas.
    
    ATURAN BAHASA:
    Gunakan BAHASA INDONESIA yang baku dan profesional.
    
    Output WAJIB JSON:
    {{
        "signal": "BUY / SELL",
        "confidence": "High / Medium / Low",
        "math_explanation": "Jelaskan analisa kamu berdasarkan data pendukung (ADP, ISM, JOLTs) untuk memprediksi NFP besok.",
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
