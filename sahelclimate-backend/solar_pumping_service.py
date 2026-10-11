from datetime import datetime, time

def optimize_solar_pumping(required_water_m3: float, pump_flow_rate_m3_h: float = 15.0, peak_sun_hours: float = 6.0):
    """
    Optimise le calendrier de pompage solaire en fonction du volume d'eau requis,
    du débit de la pompe (m³/h) et des heures d'ensoleillement optimal au Sahel.
    
    - required_water_m3 : Volume d'irrigation nécessaire (m³)
    - pump_flow_rate_m3_h : Débit nominal de la pompe solaire (ex: 15 m³/h)
    - peak_sun_hours : Nombre d'heures d'ensoleillement optimal par jour (moyenne au Sahel ~ 5.5 à 7h)
    """
    
    # 1. Calcul du temps total de pompage nécessaire en heures
    if pump_flow_rate_m3_h <= 0:
        total_pumping_hours = 0.0
    else:
        total_pumping_hours = required_water_m3 / pump_flow_rate_m3_h
        
    # 2. Vérification de faisabilité par rapport à l'ensoleillement disponible
    max_daily_capacity = pump_flow_rate_m3_h * peak_sun_hours
    is_feasible_in_one_day = required_water_m3 <= max_daily_capacity
    
    # 3. Détermination de la plage horaire optimale de pompage au Sahel
    # Au Sahel, le rendement solaire photovoltaïque est maximal entre 10h00 et 16h00.
    # On centre la plage de pompage autour de midi solaire (11h00 - 15h00 par défaut).
    start_hour = 10.0  # 10h00
    optimal_start_time = "10:00"
    
    if total_pumping_hours <= peak_sun_hours:
        # Tout le volume peut être pompé pendant les heures d'ensoleillement optimal
        end_hour = start_hour + total_pumping_hours
        running_hours_desc = f"De {optimal_start_time} à {int(end_hour):02d}:{int((end_hour % 1) * 60):02d}"
        efficiency_status = "OPTIMAL_SOLAR_MATCH"
        advice = "Le pompage peut être entièrement alimenté par l'énergie solaire directe sans solliciter de batteries."
    else:
        # Le volume est trop important pour une seule journée ou dépasse les heures de pic
        excess_hours = total_pumping_hours - peak_sun_hours
        running_hours_desc = f"De 09:30 à 16:00 (Plage solaire maximale)"
        efficiency_status = "WARNING_CAPACITY_EXCEEDED"
        advice = f"Attention : Le volume d'eau requis nécessite {total_pumping_hours:.1f}h de pompage, ce qui dépasse la fenêtre de plein ensoleillement ({peak_sun_hours}h). Envisagez d'étaler l'irrigation sur 2 jours ou d'augmenter la capacité PV."

    return {
        "required_water_m3": round(required_water_m3, 2),
        "pump_flow_rate_m3_h": pump_flow_rate_m3_h,
        "total_pumping_hours_needed": round(total_pumping_hours, 2),
        "recommended_time_window": running_hours_desc,
        "is_feasible_in_one_day": is_feasible_in_one_day,
        "efficiency_status": efficiency_status,
        "advice": advice,
        "energy_source": "Solaire Photovoltaïque (PV Direct)"
    }
