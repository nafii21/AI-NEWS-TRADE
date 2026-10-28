# ====================================================
# DASHBOARD MAKRO MANUAL - FOKUS FOMC
# Update angka Actual, Forecast, Previous terbaru sebelum Run
# ====================================================
MANUAL_DASHBOARD = {
    # --- INFLASI (Paling krusial buat FOMC) ---
    "CPI": {
        "actual": 3.7, "forecast": 3.6, "previous": 3.4, "date": "Sep-26"
    },
    "Core CPI": {
        "actual": 2.6, "forecast": 2.5, "previous": 2.4, "date": "Sep-26"
    },
    "PPI": {
        "actual": 1.3, "forecast": 0.5, "previous": 0.4, "date": "Sep-26"
    },
    "Core PCE": {
        "actual": 3.0, "forecast": 3.1, "previous": 3.7, "date": "Aug-26"
    },

    # --- TENAGA KERJA (Nentuin apakah Fed berani Hawkish) ---
    "NFP": {
        "actual": 178.0, "forecast": 60.0, "previous": -133.0, "date": "Mar-26"
    },
    "Unemployment Rate": {
        "actual": 4.2, "forecast": 4.1, "previous": 4.1, "date": "Sep-26"
    },
    "ADP Employment": {
        "actual": 109.0, "forecast": 100.0, "previous": 62.0, "date": "Apr-26"
    },
    "Average Hourly Earnings": {
        "actual": 3.5, "forecast": 3.7, "previous": 3.8, "date": "Mar-26"
    },

    # --- PERTUMBUHAN & KONSUMEN ---
    "GDP": {
        "actual": 2.2, "forecast": 2.0, "previous": 2.5, "date": "Q2-26"
    },
    "Retail Sales": {
        "actual": -0.2, "forecast": 0.4, "previous": 0.4, "date": "Jan-26"
    },
    "Consumer Confidence": {
        "actual": 84.5, "forecast": 90.0, "previous": 84.5, "date": "Feb-26"
    }
}
