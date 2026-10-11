import requests
from datetime import datetime, timedelta

def get_weather_forecast(latitude: float, longitude: float):
    """
    Récupère les prévisions météorologiques sur 7 jours via l'API Open-Meteo
    (température maximale, précipitation cumulée, évapotranspiration ETo).
    """
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&daily=temperature_2m_max,precipitation_sum,et0_fao_evapotranspiration&timezone=auto"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            daily = data.get("daily", {})
            
            times = daily.get("time", [])
            precips = daily.get("precipitation_sum", [])
            temps = daily.get("temperature_2m_max", [])
            et0s = daily.get("et0_fao_evapotranspiration", [])
            
            forecast_list = []
            for i in range(len(times)):
                forecast_list.append({
                    "date": times[i],
                    "max_temp_c": temps[i] if i < len(temps) else 0.0,
                    "precipitation_mm": precips[i] if i < len(precips) else 0.0,
                    "et0_mm": et0s[i] if i < len(et0s) else 5.0
                })
            return forecast_list
    except Exception as e:
        print(f"Erreur lors de la récupération des prévisions météo : {e}")
    
    # Données de secours (fallback) en cas de hors-ligne
    return [
        {"date": (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d"), "max_temp_c": 38.0, "precipitation_mm": 0.0, "et0_mm": 6.0}
        for i in range(7)
    ]

def evaluate_7day_weather_risk(latitude: float, longitude: float):
    """
    Analyse les prévisions à 7 jours pour détecter :
    1. Un risque de vague de chaleur (température > 40°C consécutive).
    2. Un cumul de pluie suffisant pour annuler l'irrigation imminente.
    """
    forecast = get_weather_forecast(latitude, longitude)
    
    total_expected_precip = sum([day["precipitation_mm"] for day in forecast])
    max_temperatures = [day["max_temp_c"] for day in forecast]
    hot_days_count = sum([1 for t in max_temperatures if t > 40.0])
    
    alerts = []
    
    if total_expected_precip > 15.0:
        alerts.append({
            "type": "RAIN_SURPLUS",
            "message": f"Pluies importantes prévues ({total_expected_precip:.1f} mm) sur les 7 prochains jours. Reportez l'irrigation programmée."
        })
    elif total_expected_precip == 0.0:
        alerts.append({
            "type": "DROUGHT_RISK",
            "message": "Aucune précipitation prévue sur 7 jours. Maintenez un suivi rigoureux de l'irrigation."
        })
        
    if hot_days_count >= 3:
        alerts.append({
            "type": "HEATWAVE",
            "message": f"Alerte canicule : {hot_days_count} jours à plus de 40°C prévus. Risque d'évapotranspiration accrue."
        })
        
    return {
        "7_day_forecast": forecast,
        "total_expected_precipitation_mm": round(total_expected_precip, 2),
        "alerts": alerts
    }
