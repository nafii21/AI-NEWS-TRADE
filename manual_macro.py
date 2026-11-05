# ====================================================
# 1. DASHBOARD MAKRO (Data Historis buat bahan analisa AI)
# Data Riil per 5 November 2026
# ====================================================
MANUAL_DASHBOARD = {
    # --- TENAGA KERJA ---
    "NFP": {
        "actual": 29.0,       
        "forecast": 89.0,     
        "previous": 133.0,    
        "date": "Sep-26"
    },
    "ADP Employment": {
        "actual": 86.0,       
        "forecast": 67.0,     
        "previous": 86.0,     
        "date": "Okt-26"
    },
    "Challenger Job Cuts": {
        "actual": 75.5,       # Actual PHK Okt-26
        "forecast": 60.0,     # Ekspektasi pasar
        "previous": 72.8,     # Previous (Sep-26)
        "date": "Okt-26"
    },
    "JOLTs Job Openings": {
        "actual": 7523.0,     
        "forecast": 7100.0,   
        "previous": 7190.0,   
        "date": "Sep-26"
    },
    "Unemployment Rate": {
        "actual": 4.2,        
        "forecast": 4.2,      
        "previous": 4.1,      
        "date": "Okt-26"
    },
    "Average Hourly Earnings": {
        "actual": 0.1,        
        "forecast": 0.3,      
        "previous": 0.3,      
        "date": "Okt-26"
    },
    "Jobless Claims": {
        "actual": 194.0,      
        "forecast": 200.0,    
        "previous": 200.0,    
        "date": "Okt-26"
    },

    # --- INFLASI ---
    "CPI": {"actual": 3.7, "forecast": 3.6, "previous": 3.4, "date": "Sep-26"},
    "Core CPI": {"actual": 2.6, "forecast": 2.5, "previous": 2.4, "date": "Sep-26"},
    "PPI": {"actual": 6.3, "forecast": 5.3, "previous": 5.6, "date": "Sep-26"},
    "Core PCE": {"actual": 3.0, "forecast": 3.1, "previous": 3.0, "date": "Sep-26"},

    # --- PERTUMBUHAN & KONSUMEN ---
    "GDP": {"actual": 3.4, "forecast": 3.1, "previous": 2.2, "date": "Q3-26"},
    "Retail Sales": {"actual": 0.8, "forecast": 0.3, "previous": 1.3, "date": "Sep-26"},
    "Consumer Confidence": {"actual": 91.7, "forecast": 80.4, "previous": 84.2, "date": "Okt-26"}
}

# ====================================================
# 2. AGENDA RILIS BESOK (NFP 6 Nov 2026)
# ====================================================
UPCOMING_EVENTS = [
    {
        "title": "NFP (Non-Farm Payrolls)",
        "date_utc": "2026-11-06 12:30:00", # 19:30 WIB (sesuai output lu)
        "forecast": 63.0,                  # Sesuai Investing.com
        "previous": 29.0
    }
]
