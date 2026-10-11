def optimize_solar_pumping(required_water_m3: float, pump_flow_rate_m3_h: float = 15.0, peak_sun_hours: float = 6.0):
    total_pumping_hours = 0.0 if pump_flow_rate_m3_h <= 0 else required_water_m3 / pump_flow_rate_m3_h
    max_daily_capacity = pump_flow_rate_m3_h * peak_sun_hours
    is_feasible_in_one_day = required_water_m3 <= max_daily_capacity
    
    start_hour = 10.0
    optimal_start_time = "10:00"

    if total_pumping_hours <= peak_sun_hours:
        end_hour = start_hour + total_pumping_hours
        running_hours_desc = f"De {optimal_start_time} à {int(end_hour):02d}:{int((end_hour % 1) * 60):02d}"
        efficiency_status = "OPTIMAL_SOLAR_MATCH"
        advice = "Le pompage peut être entièrement alimenté par l'énergie solaire directe."
    else:
        running_hours_desc = "De 09:30 à 16:00 (Plage solaire maximale)"
        efficiency_status = "WARNING_CAPACITY_EXCEEDED"
        advice = f"Attention : Le volume requiert {total_pumping_hours:.1f}h de pompage, dépassant la fenêtre optimale ({peak_sun_hours}h)."

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
