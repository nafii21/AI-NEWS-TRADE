def calculate_surprise_score(actual, forecast, sigma_consensus):
    if sigma_consensus == 0: return 0.0
    s_t = (actual - forecast) / sigma_consensus
    return round(s_t, 2)

def get_historical_sigma(news_title):
    title = news_title.upper()
    if "NON-FARM" in title or "NFP" in title: return 70.0
    elif "ADP" in title: return 50.0
    elif "JOBLESS" in title or "UNEMPLOYMENT" in title: return 15.0
    elif "CPI" in title or "CONSUMER PRICE" in title: return 0.2
    elif "PPI" in title or "PRODUCER PRICE" in title: return 0.3
    elif "PCE" in title: return 0.2
    elif "AVERAGE HOURLY" in title or "EARNINGS" in title: return 0.1
    elif "FOMC" in title or "FEDERAL FUNDS" in title: return 25.0
    elif "GDP" in title: return 0.5
    elif "RETAIL SALES" in title: return 0.4
    return 1.0

def build_pre_news_quant(news_title, forecast, previous, supporting_data):
    main_sigma = get_historical_sigma(news_title)
    main_surprise_score = calculate_surprise_score(forecast, previous, main_sigma)
    
    context = {
        "main_surprise_score": main_surprise_score,
        "supporting_analysis": {}
    }
    
    for data_name, data_val in supporting_data.items():
        try:
            act_val = float(data_val.get('actual', 0))
            fcst_val = float(data_val.get('forecast', 0))
            prev_val = float(data_val.get('previous', 0))
            sup_sigma = get_historical_sigma(data_name)
            
            # Jika data sudah rilis (Actual != 0)
            if act_val != 0:
                sup_score = calculate_surprise_score(act_val, fcst_val, sup_sigma)
                desc = f"Actual: {act_val} vs Fcst: {fcst_val}"
            else:
                # Jika belum rilis
                sup_score = calculate_surprise_score(fcst_val, prev_val, sup_sigma)
                desc = f"Fcst: {fcst_val} vs Prev: {prev_val}"
                
            context['supporting_analysis'][data_name] = {
                "score": sup_score,
                "desc": desc,
                "date": data_val.get('date')
            }
        except: pass
            
    return context
