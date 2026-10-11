CROP_FAO_DATA = {
    "Maïs": {"stages": [20, 35, 40, 30], "kc": [0.30, 1.20, 0.60]},
    "Sorgho": {"stages": [20, 35, 45, 30], "kc": [0.30, 1.00, 0.55]},
    "Millet": {"stages": [15, 30, 40, 25], "kc": [0.30, 1.00, 0.40]},
    "Riz": {"stages": [30, 30, 60, 30], "kc": [1.05, 1.20, 0.75]},
    "Coton": {"stages": [30, 50, 55, 45], "kc": [0.35, 1.15, 0.70]},
    "Maraîchage": {"stages": [25, 30, 40, 25], "kc": [0.35, 1.05, 0.90]}
}

def get_dynamic_kc(crop_type: str, days_after_planting: int) -> float:
    if crop_type not in CROP_FAO_DATA:
        return 1.05
    data = CROP_FAO_DATA[crop_type]
    stages, (kc_ini, kc_mid, kc_end) = data["stages"], data["kc"]
    l_ini, l_dev, l_mid, l_end = stages
    total_duration = sum(stages)

    if days_after_planting >= total_duration:
        return kc_end
    if days_after_planting <= l_ini:
        return kc_ini
    elif days_after_planting <= (l_ini + l_dev):
        return kc_ini + ((days_after_planting - l_ini) / l_dev) * (kc_mid - kc_ini)
    elif days_after_planting <= (l_ini + l_dev + l_mid):
        return kc_mid
    else:
        return kc_mid + ((days_after_planting - (l_ini + l_dev + l_mid)) / l_end) * (kc_end - kc_mid)

def calculate_fao56_water_balance(et0_mm: float, precipitation_mm: float, crop_type: str, days_after_planting: int = 45, area_ha: float = 1.0):
    kc = get_dynamic_kc(crop_type, days_after_planting)
    etc_mm = et0_mm * kc
    effective_precip = precipitation_mm * 0.8
    deficit_mm = max(0.0, etc_mm - effective_precip)
    recommended_irrigation_m3 = deficit_mm * area_ha * 10.0
    return {
        "crop_type": crop_type,
        "days_after_planting": days_after_planting,
        "current_kc": round(kc, 2),
        "et0_mm": round(et0_mm, 2),
        "etc_mm": round(etc_mm, 2),
        "precipitation_mm": round(precipitation_mm, 2),
        "deficit_mm": round(deficit_mm, 2),
        "recommended_irrigation_m3": round(recommended_irrigation_m3, 2),
        "status": "IRRIGATION_NEEDED" if deficit_mm > 0 else "SUFFICIENT_WATER"
    }
