import math

def calculate_surprise_score(actual, forecast, sigma_consensus):
    """
    Rumus Standar Institusi: S_t = (A_t - E_t) / Sigma_consensus
    """
    if sigma_consensus == 0:
        return 0.0
    
    s_t = (actual - forecast) / sigma_consensus
    return round(s_t, 2)

def get_historical_sigma(news_title):
    """
    Nilai Standar Deviasi (Sigma) historis per jenis berita.
    (Ini angka riil rata-rata deviasi analis terhadap rilis data AS)
    """
    if "Non-Farm" in news_title:
        return 70.0  # NFP biasanya bergerak +/- 70K dari tebakan
    elif "CPI" in news_title:
        return 0.2    # CPI biasanya bergerak +/- 0.2% dari tebakan
    elif "ADP" in news_title:
        return 50.0
    return 1.0

def build_pre_news_quant(news_title, forecast, previous, supporting_data):
    """
    Menghitung Pre-News Surprise Score (Modifikasi).
    Kita bandingin seberapa jauh Ekspektasi (Forecast) bergeser dari Bulan Lalu (Previous).
    """
    sigma = get_historical_sigma(news_title)
    
    # 1. Hitung Expected Surprise (Pergeseran Ekspektasi)
    expected_surprise_score = calculate_surprise_score(forecast, previous, sigma)
    
    context = {
        "main_surprise_score": expected_surprise_score,
        "supporting_analysis": {}
    }
    
    # 2. Hitung "Realitas" dari data pendukung (Misal ADP vs NFP)
    # Kalau NFP Forecast naik (Expected Surprise +), tapi ADP anjlok, ini konflik!
    for data_name, data_val in supporting_data.items():
        try:
            f_val = float(data_val['forecast'])
            p_val = float(data_val['previous'])
            sup_sigma = get_historical_sigma(data_name)
            sup_score = calculate_surprise_score(f_val, p_val, sup_sigma)
            context['supporting_analysis'][data_name] = sup_score
        except:
            pass
            
    return context
