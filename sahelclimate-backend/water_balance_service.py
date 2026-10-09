import math
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WaterBalanceService")

# Coefficients culturaux FAO-56 pour les cultures clés du Sahel
CROP_KC_TABLE = {
    "Maïs": {"initial": 0.3, "dev": 0.7, "mid": 1.2, "late": 0.6},
    "Sorgho": {"initial": 0.3, "dev": 0.65, "mid": 1.05, "late": 0.55},
    "Sésame": {"initial": 0.35, "dev": 0.7, "mid": 1.1, "late": 0.25},
    "Arachide": {"initial": 0.4, "dev": 0.75, "mid": 1.15, "late": 0.6},
    "Niébé": {"initial": 0.4, "dev": 0.7, "mid": 1.05, "late": 0.5}
}

class WaterBalanceEngine:
    """
    Moteur de calcul du bilan hydrique selon la méthodologie FAO-56.
    """

    @staticmethod
    def calculate_et0(t_mean: float, t_max: float, t_min: float, rh_mean: float, wind_speed_2m: float, solar_rad: float = 22.0) -> float:
        """
        Calcul simplifié d'Évapotranspiration de référence (ET0 en mm/jour) 
        basé sur l'équation d'Hargreaves / Penman-Monteith simplifiée FAO-56.
        """
        # Formule d'Hargreaves adaptée aux zones arides/sahéliennes
        # ET0 = 0.0023 * (Tmean + 17.8) * (Tmax - Tmin)^0.5 * Ra
        # Ra estimé via solar_rad
        temp_range = max(t_max - t_min, 1.0)
        et0 = 0.0023 * (t_mean + 17.8) * math.sqrt(temp_range) * (solar_rad * 0.408)
        return round(max(et0, 1.5), 2)

    @classmethod
    def get_crop_kc(cls, crop_type: str, growth_stage: str) -> float:
        """
        Récupère le coefficient cultural (Kc) selon la culture et son stade phénologique.
        Stades valides: 'initial', 'dev', 'mid', 'late'
        """
        crop_data = CROP_KC_TABLE.get(crop_type, CROP_KC_TABLE["Sorgho"])
        return crop_data.get(growth_stage, 0.8)

    @classmethod
    def compute_irrigation_needs(
        cls,
        crop_type: str,
        growth_stage: str,
        area_ha: float,
        t_mean: float = 34.0,
        t_max: float = 40.0,
        t_min: float = 28.0,
        rh_mean: float = 25.0,
        wind_speed: float = 3.2,
        effective_rain_mm: float = 0.0
    ) -> Dict[str, Any]:
        """
        Calcule le bilan hydrique complet et les besoins d'irrigation hebdomadaires.
        """
        # 1. Calcul ET0 journalier
        et0_daily = cls.calculate_et0(t_mean, t_max, t_min, rh_mean, wind_speed)
        
        # 2. Obtenir Kc
        kc = cls.get_crop_kc(crop_type, growth_stage)
        
        # 3. Calcul ETc journalier et hebdomadaire
        etc_daily = round(et0_daily * kc, 2)
        etc_weekly = round(etc_daily * 7, 2)
        
        # 4. Pluie efficace hebdomadaire (Méthode USDA SCS : Peff = P * 0.8 si P > 5mm)
        eff_rain_weekly = round(effective_rain_mm * 0.8 if effective_rain_mm > 5.0 else 0.0, 2)
        
        # 5. Besoin en eau net (mm/semaine et m³/ha)
        net_water_need_mm = max(0.0, round(etc_weekly - eff_rain_weekly, 2))
        water_volume_m3_per_ha = round(net_water_need_mm * 10, 2)  # 1 mm = 10 m³/ha
        total_volume_m3 = round(water_volume_m3_per_ha * area_ha, 2)

        return {
            "crop_type": crop_type,
            "growth_stage": growth_stage,
            "et0_daily_mm": et0_daily,
            "kc_coefficient": kc,
            "etc_daily_mm": etc_daily,
            "etc_weekly_mm": etc_weekly,
            "effective_rain_weekly_mm": eff_rain_weekly,
            "water_need_weekly_mm": net_water_need_mm,
            "water_volume_m3_ha": water_volume_m3_per_ha,
            "total_parcel_volume_m3": total_volume_m3,
            "irrigation_frequency": "2 à 3 fois par semaine" if net_water_need_mm > 30 else "1 à 2 fois par semaine"
        }
