def calculate_surprise_score(actual, forecast, sigma_consensus):
    if sigma_consensus == 0 or forecast == 0: 
        return 0.0
    s_t = (actual - forecast) / sigma_consensus
    return round(s_t, 2)

def get_historical_sigma(news_title):
    title = news_title.upper()
    
    # --- TENAGA KERJA ---
    if "NON-FARM" in title or "NFP" in title: 
        return 70.0
    elif "ADP" in title: 
        return 50.0
    elif "JOBLESS" in title: 
        return 15.0
    elif "UNEMPLOYMENT" in title: 
        return 0.15   
    elif "CHALLENGER" in title or "JOB CUTS" in title: 
        return 30.0 
    elif "JOLTS" in title or "JOB OPENINGS" in title: 
        return 200.0
    elif "ISM" in title: 
        return 5.0
    
    # --- INFLASI ---
    elif "CORE CPI" in title: 
        return 0.15
    elif "CPI" in title: 
        return 0.20
    elif "CORE PPI" in title: 
        return 0.25
    elif "PPI" in title: 
        return 0.30
    elif "PCE" in title: 
        return 0.20
    elif "AVERAGE HOURLY" in title: 
        return 0.10
        
    # --- KOMPONEN CPI (FOOD & SHELTER) ---
    elif "FOOD AT HOME" in title: return 0.2
    elif "CRB FOODSTUFFS" in title: return 2.0
    elif "CPI RENT" in title: return 0.1
    elif "CPI OER" in title: return 0.1
    elif "CASE-SHILLER" in title: return 0.5
        
    # --- SUKU BUNGA & PERTUMBUHAN ---
    elif "FOMC" in title or "FEDERAL FUNDS" in title: 
        return 0.25
    elif "GDP" in title: 
        return 0.50
    elif "RETAIL SALES" in title: 
        return 0.50
    elif "CONSUMER CONFIDENCE" in title: 
        return 10.0
    return 1.0

def build_pre_news_quant(news_title, forecast, previous, supporting_data):
    main_sigma = get_historical_sigma(news_title)
    main_surprise_score = calculate_surprise_score(forecast, previous, main_sigma)
    
    context = {
        "main_forecast": forecast,     
        "main_previous": previous,     
        "main_surprise_score": main_surprise_score,
        "supporting_analysis": {}
    }
    
    for data_name, data_val in supporting_data.items():
        try:
            name_upper = data_name.upper()
            act_val = float(data_val.get('actual', 0))
            fcst_val = float(data_val.get('forecast', 0))
            prev_val = float(data_val.get('previous', 0))
            sup_sigma = get_historical_sigma(data_name)
            
            if act_val != 0:
                if fcst_val != 0:
                    sup_score = calculate_surprise_score(act_val, fcst_val, sup_sigma)
                    desc = f"Actual: {act_val} vs Fcst: {fcst_val}"
                else:
                    sup_score = 0.0
                    desc = f"Actual: {act_val} (Fcst N/A)"
            else:
                sup_score = calculate_surprise_score(fcst_val, prev_val, sup_sigma)
                desc = f"Fcst: {fcst_val} vs Prev: {prev_val}"

            # Dibalikin buat indikator yang makin tinggi makin jelek
            if any(k in name_upper for k in ["JOBLESS", "UNEMPLOYMENT", "CHALLENGER", "JOB CUTS"]):
                sup_score = sup_score * -1 
                
            context['supporting_analysis'][data_name] = {
                "score": sup_score,
                "desc": desc,
                "date": data_val.get('date')
            }
        except: 
            pass
            
    return context
