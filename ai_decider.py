import requests
import os
import json
import re

def get_ai_decision(news_title, quant_context, market_context):
    api_key = os.getenv("SAKELAR_API_KEY")
    url = "https://api.sakelar.web.id/v1/chat/completions"
    model_name = "gpt-6-astra"
    
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
    2. CATATAN PENTING (LEADING INDICATORS LENGKAP): 
       Data Actual historis dari berita utama sengaja tidak dimasukkan karena sudah *priced in*. Fokus analisa kamu adalah membandingkan *Forecast* yang akan rilis besok dengan data *Leading Indicator* yang komprehensif sesuai jenis beritanya:
       - JIKA NFP: Fokus 100% pada data Tenaga Kerja (ADP Employment, ISM Manufacturing Employment, ISM Services Employment, JOLTs Job Openings, Challenger Job Cuts, Unemployment Rate, Average Hourly Earnings, Jobless Claims).
       - JIKA CPI: Fokus 100% pada data Inflasi (PPI, Core PPI, Core PCE, AHE/Wage-Push, Shelter/Rent & OER, Food at Home, CRB Foodstuffs, Case-Shiller).
       - JIKA FOMC: Fokus pada gabungan data Inflasi (CPI/PPI/PCE) sebagai prioritas utama, dan data Tenaga Kerja (NFP/ADP/Unemployment) sebagai konfirmasi.
    3. ATURAN FILTER DOMAIN (SANGAT PENTING):
       - JIKA BERITA UTAMA ADALAH NFP: ABAIKAN total data Inflasi (CPI/PPI/PCE).
       - JIKA BERITA UTAMA ADALAH CPI: ABAIKAN total data Tenaga Kerja murni seperti NFP/ADP/JOLTs (Kecuali AHE, karena AHE adalah pemicu inflasi upah).
       - JIKA BERITA UTAMA ADALAH FOMC: Gunakan data Inflasi sebagai prioritas, lalu Tenaga Kerja sebagai konfirmasi.
    4. ATURAN KHUSUS CPI (KORELASI KOMPONEN):
       - UPAH / AHE: Ini adalah data Inflasi (Wage-Push), BUKAN tenaga kerja biasa. Jika AHE Actual > Forecast, upah naik -> inflasi jasa naik -> Hawkish (SELL Gold).
       - SHELTER (Rent & OER): Menyumbang ~40% CPI. Jika Skor Positif, ada tekanan inflasi struktural (SELL Gold).
       - FOOD (Food at Home & CRB): Menyumbang ~13% CPI. Jika naik, konfirmasi inflasi pangan memanas (SELL Gold).
       - CASE-SHILLER: Leading indicator untuk Shelter. Jika turun, tekanan sewa reda (Dovish).
    5. JANGAN MENJUMLAHKAN ATAU MERATA-RATA SKOR. Nilai data mana yang paling dominan untuk memprediksi apakah {news_title} besok akan mencapai {quant_context.get('main_forecast', 0.0)} atau tidak.
    6. KONTEKS MARKET: DXY naik = konfirmasi SELL. DXY turun = konfirmasi BUY. Minyak naik = Inflasi naik = SELL.
    7. CONFIDENCE: Berikan "High" HANYA JIKA semua data pendukung di domain tersebut searah. Jika campur aduk, WAJIB berikan "Medium".
    
    Tugasmu:
    Tentukan arah XAUUSD dengan tegas (BUY/SELL) berdasarkan prediksi {news_title} besok dari data pendukung di atas.
    
    ATURAN BAHASA:
    Gunakan BAHASA INDONESIA yang baku dan profesional.
    
    Output WAJIB JSON:
    {{
        "signal": "BUY / SELL",
        "confidence": "High / Medium / Low",
        "math_explanation": "Jelaskan analisa kamu berdasarkan data pendukung yang relevan (misal: PPI, AHE, Shelter untuk CPI; atau ADP, JOLTs untuk NFP) untuk memprediksi {news_title} besok.",
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
        response = requests.post(url, json=payload, headers=headers, timeout=120)
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
