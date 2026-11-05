# ====================================================
# DASHBOARD MAKRO MANUAL - PERIODE RILIS 7 AGUSTUS 2026
# ====================================================
MANUAL_DASHBOARD = {
    # --- TENAGA KERJA (Data Juli 2026) ---
    "NFP": {
        "actual": -23.0,       # Actual -23K (Kontraksi)
        "forecast": 85.0,      # Ekspektasi 85K
        "previous": 20.0,      # Bulan lalu (Juni): 20K
        "date": "Jul-26"
    },
    "ADP Employment": {
        "actual": 122.0,       # ADP Juli: 122K
        "forecast": 150.0,     # Ekspektasi 150K
        "previous": 155.0,     # Juni: 155K
        "date": "Jul-26"
    },
    "Challenger Job Cuts": {
        "actual": 50.0,        # PHK Juli
        "forecast": 45.0,      
        "previous": 40.0,      
        "date": "Jul-26"
    },
    "JOLTs Job Openings": {
        "actual": 7400.0,      # JOLTs Juni
        "forecast": 7500.0,    
        "previous": 7600.0,    
        "date": "Jun-26"
    },
    "Unemployment Rate": {
        "actual": 4.2,         # Unemployment Juli
        "forecast": 4.1,       
        "previous": 4.1,       
        "date": "Jul-26"
    },
    "Average Hourly Earnings": {
        "actual": 0.3,         # AHE Juli MoM
        "forecast": 0.3,       
        "previous": 0.4,       
        "date": "Jul-26"
    },
    "Jobless Claims": {
        "actual": 220.0,       
        "forecast": 215.0,     
        "previous": 210.0,     
        "date": "Jul-26"
    },

    # --- INFLASI ---
    "CPI": {"actual": 3.4, "forecast": 3.4, "previous": 3.4, "date": "Jul-26"},
    "Core CPI": {"actual": 2.4, "forecast": 2.4, "previous": 2.5, "date": "Jul-26"},
    "PPI": {"actual": 0.1, "forecast": 0.2, "previous": 0.2, "date": "Jul-26"},
    "Core PCE": {"actual": 3.3, "forecast": 3.3, "previous": 3.3, "date": "Jul-26"},

    # --- PERTUMBUHAN & KONSUMEN ---
    "GDP": {"actual": 2.2, "forecast": 2.1, "previous": 2.0, "date": "Q2-26"},
    "Retail Sales": {"actual": 0.6, "forecast": 0.4, "previous": 0.3, "date": "Jul-26"},
    "Consumer Confidence": {"actual": 90.8, "forecast": 91.5, "previous": 92.0, "date": "Jul-26"}
}

# ====================================================
# AGENDA RILIS 7 AGUSTUS 2026
# ====================================================
UPCOMING_EVENTS = [
    {
        "title": "NFP (Non-Farm Payrolls)",
        "date_utc": "2026-08-07 12:30:00", # Rilis 7 Agustus
        "forecast": 85.0,                  
        "previous": 20.0
    }
]
