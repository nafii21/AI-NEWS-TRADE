# ====================================================
# 1. DASHBOARD MAKRO (Data Historis buat bahan analisa AI)
# ====================================================
MANUAL_DASHBOARD = {
    # --- TENAGA KERJA ---
    "NFP (Sep-26)": {
        "actual": 29.0,       # Rilis 2 Okt
        "forecast": 89.0,     # Konsensus saat itu
        "previous": 133.0,    # Previous (Agustus)
        "date": "Sep-26"
    },
    "ADP Employment (Okt-26)": {
        "actual": 86.0,       # Rilis 4 Nov
        "forecast": 67.0,     
        "previous": 86.0,     
        "date": "Okt-26"
    },
    "JOLTs Job Openings (Sep-26)": {
        "actual": 7523.0,     # Rilis 3 Nov
        "forecast": 7100.0,   
        "previous": 7190.0,   
        "date": "Sep-26"
    },
    "Unemployment Rate (Okt-26)": {
        "actual": 4.2,        
        "forecast": 4.2,      
        "previous": 4.1,      
        "date": "Okt-26"
    },
    "Average Hourly Earnings (Okt-26)": {
        "actual": 0.1,        
        "forecast": 0.3,      
        "previous": 0.3,      
        "date": "Okt-26"
    },
    "Jobless Claims (Okt-26)": {
        "actual": 194.0,      
        "forecast": 200.0,    
        "previous": 200.0,    
        "date": "Okt-26"
    },

    # --- INFLASI ---
    "CPI (Sep-26)": {"actual": 3.7, "forecast": 3.6, "previous": 3.4, "date": "Sep-26"},
    "Core CPI (Sep-26)": {"actual": 2.6, "forecast": 2.5, "previous": 2.4, "date": "Sep-26"},
    "PPI (Sep-26)": {"actual": 6.3, "forecast": 5.3, "previous": 5.6, "date": "Sep-26"},
    "Core PCE (Sep-26)": {"actual": 3.0, "forecast": 3.1, "previous": 3.0, "date": "Sep-26"},

    # --- PERTUMBUHAN & KONSUMEN ---
    "GDP (Q3-26)": {"actual": 3.4, "forecast": 3.1, "previous": 2.2, "date": "Q3-26"},
    "Retail Sales (Sep-26)": {"actual": 0.8, "forecast": 0.3, "previous": 1.3, "date": "Sep-26"},
    "Consumer Confidence (Okt-26)": {"actual": 91.7, "forecast": 80.4, "previous": 84.2, "date": "Okt-26"}
}

# ====================================================
# 2. AGENDA RILIS BESOK (Manual Override)
# Isi di sini biar bot gak nebak-nebak pakai data FF yang suka 0.0
# ====================================================
UPCOMING_EVENTS = [
    {
        "title": "NFP (Non-Farm Payrolls)",
        "date_utc": "2026-11-06 12:30:00", # 20:30 WIB
        "forecast": 63.0,                  # Sesuai Investing.com
        "previous": 29.0
    }
]
