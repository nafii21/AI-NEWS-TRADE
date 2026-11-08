# ====================================================
# DASHBOARD MAKRO MANUAL - UPDATE PPI MoM (8 NOV 2026)
# ====================================================
MANUAL_DASHBOARD = {
    # --- TENAGA KERJA ---
    "NFP": {
        "actual": 165.0, "forecast": 65.0, "previous": 60.0, "date": "Okt-26"
    },
    "ADP Employment": {
        "actual": 86.0, "forecast": 67.0, "previous": 86.0, "date": "Okt-26"
    },
    "ISM Employment Index": {
        "actual": 46.8, "forecast": 47.5, "previous": 45.4, "date": "Okt-26"
    },
    "Challenger Job Cuts": {
        "actual": 43.99, "forecast": 50.0, "previous": 43.28, "date": "Okt-26"
    },
    "JOLTs Job Openings": {
        "actual": 7523.0, "forecast": 7100.0, "previous": 7190.0, "date": "Sep-26"
    },
    "Unemployment Rate": {
        "actual": 4.1, "forecast": 4.2, "previous": 4.2, "date": "Okt-26"
    },
    "Average Hourly Earnings": {
        "actual": 0.4, "forecast": 0.3, "previous": 0.1, "date": "Okt-26"
    },
    "Jobless Claims": {
        "actual": 189.0, "forecast": 196.0, "previous": 194.0, "date": "Okt-26"
    },

    # --- INFLASI (PAKAI MoM SESUAI INVESTING.COM) ---
    "PPI (MoM)": {
        "actual": 1.3,         # <--- FIX: PPI MoM
        "forecast": 0.6,       
        "previous": 0.5,       
        "date": "Sep-26"
    },
    "Core PPI (MoM)": {
        "actual": 0.7,         # <--- FIX: Core PPI MoM
        "forecast": 0.3,       
        "previous": 0.2,       
        "date": "Sep-26"
    },
    "Core PCE": {
        "actual": 3.0, "forecast": 3.1, "previous": 3.0, "date": "Sep-26"
    },

    # --- KOMPONEN PANGAN & PERUMAHAN ---
    "Food at Home (MoM)": {
        "actual": -0.1, "forecast": 0.1, "previous": 0.0, "date": "Sep-26"
    },
    "CRB Foodstuffs": {
        "actual": 0.0, "forecast": 0.0, "previous": 0.0, "date": "Okt-26"
    },
    "CPI Rent (MoM)": {
        "actual": 0.2, "forecast": 0.3, "previous": 0.3, "date": "Sep-26"
    },
    "CPI OER (MoM)": {
        "actual": 0.3, "forecast": 0.4, "previous": 0.3, "date": "Sep-26"
    },
    "Case-Shiller Home Price (YoY)": {
        "actual": 0.8, "forecast": 0.9, "previous": 1.2, "date": "Mar-26"
    },

    # --- PERTUMBUHAN & KONSUMEN ---
    "GDP": {"actual": 3.4, "forecast": 3.2, "previous": 2.2, "date": "Q3-26"},
    "Retail Sales": {"actual": 0.8, "forecast": 0.3, "previous": 1.3, "date": "Sep-26"},
    "Consumer Confidence": {"actual": 91.7, "forecast": 80.4, "previous": 84.2, "date": "Okt-26"}
}

# ====================================================
# AGENDA RILIS BESOK (CPI 10 Nov 2026)
# ====================================================
UPCOMING_EVENTS = [
    {
        "title": "CPI m/m",
        "date_utc": "2026-11-10 13:30:00", # 20:30 WIB
        "forecast": 0.3,                  
        "previous": 0.6
    }
]
