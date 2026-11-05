# ====================================================
# DASHBOARD MAKRO MANUAL - KONTEKS SEBELUM RILIS 7 AGUSTUS
# ====================================================
MANUAL_DASHBOARD = {
    # --- TENAGA KERJA (Data Historis Sebelum Agustus) ---
    "NFP (Jun-26)": {
        "actual": 20.0,        # Actual NFP Juni (dirilis awal Juli)
        "forecast": 25.0,      # Ekspektasi saat itu
        "previous": 15.0,      # Previous bulan Mei
        "date": "Jun-26"
    },
    "ADP Employment (Jul-26)": {
        "actual": 122.0,       # ADP Juli (rilis 5 Agustus)
        "forecast": 150.0,     
        "previous": 155.0,     
        "date": "Jul-26"
    },
    "Challenger Job Cuts (Jul-26)": {
        "actual": 50.0,        
        "forecast": 45.0,      
        "previous": 40.0,      
        "date": "Jul-26"
    },
    "JOLTs Job Openings (Jun-26)": {
        "actual": 7400.0,      
        "forecast": 7500.0,    
        "previous": 7600.0,    
        "date": "Jun-26"
    },
    "Unemployment Rate (Jun-26)": {
        "actual": 4.1,         
        "forecast": 4.1,       
        "previous": 4.0,       
        "date": "Jun-26"
    },
    "Average Hourly Earnings (Jun-26)": {
        "actual": 0.4,         
        "forecast": 0.3,       
        "previous": 0.4,       
        "date": "Jun-26"
    },
    "Jobless Claims (Jul-26)": {
        "actual": 220.0,       
        "forecast": 215.0,     
        "previous": 210.0,     
        "date": "Jul-26"
    },

    # --- INFLASI ---
    "CPI (Jun-26)": {"actual": 3.4, "forecast": 3.4, "previous": 3.4, "date": "Jun-26"},
    "Core CPI (Jun-26)": {"actual": 2.4, "forecast": 2.4, "previous": 2.5, "date": "Jun-26"},
    "PPI (Jun-26)": {"actual": 0.1, "forecast": 0.2, "previous": 0.2, "date": "Jun-26"},
    "Core PCE (Jun-26)": {"actual": 3.3, "forecast": 3.3, "previous": 3.3, "date": "Jun-26"},

    # --- PERTUMBUHAN & KONSUMEN ---
    "GDP (Q2-26)": {"actual": 2.2, "forecast": 2.1, "previous": 2.0, "date": "Q2-26"},
    "Retail Sales (Jun-26)": {"actual": 0.6, "forecast": 0.4, "previous": 0.3, "date": "Jun-26"},
    "Consumer Confidence (Jul-26)": {"actual": 90.8, "forecast": 91.5, "previous": 92.0, "date": "Jul-26"}
}

# ====================================================
# AGENDA RILIS 7 AGUSTUS 2026 (TARGET YANG MAU DITEBAK)
# ====================================================
UPCOMING_EVENTS = [
    {
        "title": "NFP (Non-Farm Payrolls)",
        "date_utc": "2026-08-07 12:30:00",
        "forecast": 85.0,                  # Ekspektasi pasar untuk Agustus
        "previous": 20.0                   # Data bulan lalu (Juni)
    }
]
