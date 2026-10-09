import numpy as np
from app.schemas.parcel import ParcelAnalysisRequest, NDVIAnalysisResponse

class NDVIService:
    @staticmethod
    def calculate_ndvi_from_bands(nir_band: np.ndarray, red_band: np.ndarray) -> float:
        with np.errstate(divide='ignore', invalid='ignore'):
            ndvi = (nir_band - red_band) / (nir_band + red_band)
            ndvi = np.nan_to_num(ndvi, nan=0.0)
        return float(np.mean(ndvi))

    @classmethod
    def analyze_parcel_health(cls, request: ParcelAnalysisRequest) -> NDVIAnalysisResponse:
        np.random.seed(42)
        simulated_nir = np.random.uniform(0.2, 0.6, (10, 10))
        simulated_red = np.random.uniform(0.05, 0.25, (10, 10))
        
        mean_ndvi = cls.calculate_ndvi_from_bands(simulated_nir, simulated_red)
        
        drought_risk = False
        trigger_payout = False
        
        if mean_ndvi < 0.2:
            status = "Stress hydrique critique / Sol nu"
            drought_risk = True
            trigger_payout = True
            action = "Déclenchement du versement d'assurance Mobile Money."
        elif 0.2 <= mean_ndvi < 0.4:
            status = "Végétation faible ou sous stress"
            drought_risk = True
            action = "Surveillance renforcée conseillée."
        else:
            status = "Végétation saine et dense"
            action = "Aucune action requise. Développement normal."
            
        return NDVIAnalysisResponse(
            parcel_id=request.parcel_id,
            mean_ndvi=round(mean_ndvi, 3),
            status=status,
            drought_risk_detected=drought_risk,
            trigger_payout=trigger_payout,
            recommended_action=action
        )
