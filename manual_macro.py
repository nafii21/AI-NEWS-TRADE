# ====================================================
# DASHBOARD MAKRO MANUAL - UPDATE ISM EMPLOYMENT
# ====================================================
MANUAL_DASHBOARD = {
    # --- TENAGA KERJA (LEADING INDICATORS) ---
    "ADP Employment": {
        "actual": 86.0, "forecast": 67.0, "previous": 86.0, "date": "Okt-26"
    },
    "ISM Manufacturing Employment": {
        "actual": 46.8,        # Actual Okt (Employment Index)
        "forecast": 47.5,      # Ekspektasi pasar
        "previous": 45.4,      # Bulan lalu (Sep)
        "date": "Okt-26"
    },
    "Challenger Job Cuts": {
        "actual": 43.99, "forecast": 50.0, "previous": 43.28, "date": "Okt-26"
    },
    "JOLTs Job Openings": {
        "actual": 7523.0, "forecast": 7100.0, "previous": 7190.0, "date": "Sep-26"
    },
    "Unemployment Rate": {
        "actual": 4.2, "forecast": 4.1, "previous": 4.1, "date": "Sep-26"
    },
    "Average Hourly Earnings": {
        "actual": 0.1, "forecast": 0.3, "previous": 0.3, "date": "Sep-26"
    },
    "Jobless Claims": {
        "actual": 194.0, "forecast": 199.0, "previous": 195.0, "date": "Okt-26"
    },

    # --- INFLASI ---
    "CPI": {"actual": 3.7, "forecast": 3.6, "previous": 3.4, "date": "Sep-26"},
    "Core CPI": {"actual": 2.6, "forecast": 2.5, "previous": 2.4, "date": "Sep-26"},
    "PPI": {"actual": 6.3, "forecast": 5.3, "previous": 5.6, "date": "Sep-26"},
    "Core PCE": {"actual": 3.0, "forecast": 3.1, "previous": 3.0, "date": "Sep-26"},

    # --- PERTUMBUHAN & KONSUMEN ---
    "GDP": {"actual": 3.4, "forecast": 3.2, "previous": 2.2, "date": "Q3-26"},
    "Retail Sales": {"actual": 0.8, "forecast": 0.3, "previous": 1.3, "date": "Sep-26"},
    "Consumer Confidence": {"actual": 91.7, "forecast": 80.4, "previous": 84.2, "date": "Okt-26"}
}

# ====================================================
# AGENDA RILIS BESOK (NFP 6 Nov 2026)
# ====================================================
UPCOMING_EVENTS = [
    {
        "title": "NFP (Non-Farm Payrolls)",
        "date_utc": "2026-11-06 12:30:00",
        "forecast": 63.0,                  
        "previous": 29.0
    }
]
