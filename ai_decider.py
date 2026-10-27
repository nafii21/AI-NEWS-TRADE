import requests
import os
import json
import re

def get_ai_decision(news_title, quant_context, market_context):
    # --- KONFIGURASI SKAILAR ---
    api_key = os.getenv("SKAILAR_API_KEY")
    url = "https://api.sakelar.web.id/v1"
    model_name = "deepseek-v4.1-flash"  # Ganti jika dashboard Skailar pakai ID lain
    # ---------------------------
    
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
    1. Jika Forecast bernilai 0 atau "N/A", ABAIKAN perbandingan Actual vs Forecast. Fokus pada nilai Actual dan bandingkan dengan kondisi ekonomi secara umum.
    2. DATA INFLASI (CPI, PPI, PCE): Jika Actual tinggi (>3%), inflasi panas (Hawkish) -> SELL Gold. 
    3. DATA TENAGA KERJA (NFP, ADP, Unemployment): Jika Actual kuat, ekonomi solid (Hawkish) -> SELL Gold.
    4. KONTEKS MARKET: Jika DXY naik dan Minyak naik, konfirmasi kuat Gold turun (Bearish).
    
    Tugasmu:
    Gabungkan berita utama, dashboard data makro, dan kondisi market untuk memprediksi arah XAUUSD.
    
    ATURAN BAHASA (WAJIB):
    - Gunakan BAHASA INDONESIA yang baku, profesional, dan mudah dipahami.
    - Field "math_explanation" dan "trade_plan" WAJIB menggunakan Bahasa Indonesia.
    
    Output WAJIB berupa JSON valid TANPA teks tambahan, TANPA markdown block:
    {{
        "signal": "BUY / SELL / NO TRADE",
        "confidence": "High / Medium / Low",
        "math_explanation": "Jelaskan analisa makro dan korelasi datanya di sini (Bahasa Indonesia)",
        "trade_plan": "Saran eksekusi trading untuk XAUUSD (Bahasa Indonesia)"
    }}
    """
    
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": "Kamu adalah analis makro profesional yang hanya membalas dengan JSON valid."},
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
        resp = requests.post(url, json=payload, headers=headers, timeout=45).json()
        
        if "error" in resp:
            print(f"[SKAILAR ERROR] {resp['error']}")
            return {
                "signal": "ERROR",
                "math_explanation": str(resp["error"]),
                "confidence": "-",
                "trade_plan": "-"
            }
            
        raw_content = resp["choices"][0]["message"]["content"]
        clean_json = re.sub(r'```json\n?|```', '', raw_content).strip()
        return json.loads(clean_json)
        
    except Exception as e:
        print(f"[SKAILAR EXCEPTION] {e}")
        return {
            "signal": "ERROR",
            "math_explanation": f"Gagal parsing: {e}",
            "confidence": "-",
            "trade_plan": "-"
        }
