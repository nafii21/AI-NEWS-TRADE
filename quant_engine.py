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
    Angka ini didapat dari rata-rata deviasi analis terhadap rilis data AS historis.
    """
    title = news_title.upper()
    
    # Tenaga Kerja (Employment)
    if "NON-FARM" in title or "NFP" in title:
        return 70.0  # NFP bergerak +/- 70K
    elif "ADP" in title:
        return 50.0  # ADP bergerak +/- 50K
    elif "JOBLESS" in title or "UNEMPLOYMENT" in title:
        return 15.0  # Jobless Claims +/- 15K
        
    # Inflasi (Inflation)
    elif "CPI" in title or "CONSUMER PRICE" in title:
        return 0.2   # CPI bergerak +/- 0.2%
    elif "PPI" in title or "PRODUCER PRICE" in title:
        return 0.3   # PPI bergerak +/- 0.3%
        
    # Suku Bunga & Ekonomi Makro
    elif "FOMC" in title or "FEDERAL FUNDS" in title:
        return 25.0  # Biasanya ekspektasi bunga bergerak 25 bps
    elif "GDP" in title:
        return 0.5   # GDP bergerak +/- 0.5%
    elif "RETAIL SALES" in title:
        return 0.4   # Retail Sales +/- 0.4%
        
    # Default kalau berita lain
    return 1.0

def build_pre_news_quant(news_title, forecast, previous, supporting_data):
    """
    Menghitung Pre-News Surprise Score untuk Main News & Data Pendukung.
    """
    # 1. Hitung Sigma & Surprise Score untuk Berita Utama (Main Event)
    main_sigma = get_historical_sigma(news_title)
    main_surprise_score = calculate_surprise_score(forecast, previous, main_sigma)
    
    context = {
        "main_surprise_score": main_surprise_score,
        "supporting_analysis": {}
    }
    
    # 2. Hitung Surprise Score untuk semua Data Pendukung
    for data_name, data_val in supporting_data.items():
        try:
            f_val = float(data_val['forecast'])
            p_val = float(data_val['previous'])
            sup_sigma = get_historical_sigma(data_name)
            sup_score = calculate_surprise_score(f_val, p_val, sup_sigma)
            
            # Simpan hasilnya
            context['supporting_analysis'][data_name] = sup_score
        except:
            pass
            
    return context
