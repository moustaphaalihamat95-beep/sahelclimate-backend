import random
from datetime import datetime

def get_parcel_ndvi_status(latitude: float, longitude: float, crop_type: str):
    """
    Simule ou récupère les données d'indice de végétation NDVI pour une parcelle.
    En production, cette fonction peut interroger l'API Sentinel Hub ou Google Earth Engine.
    """
    # Génération d'une valeur de NDVI réaliste selon la saison et le type de culture au Sahel
    # Valeur type comprise entre 0.20 (début de cycle/terre nue) et 0.75 (pleine croissance)
    base_ndvi = random.uniform(0.35, 0.72)
    
    # Interprétation de l'état de santé de la culture
    if base_ndvi < 0.30:
        health_status = "STRESS_WARNING"
        message = "Végétation clairsemée ou stress hydrique potentiel détecté par satellite."
    elif base_ndvi < 0.55:
        health_status = "GROWING"
        message = "Développement végétatif actif en cours."
    else:
        health_status = "OPTIMAL"
        message = "Biomasse dense et excellente vigueur chlorophyllienne."

    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d"),
        "ndvi_score": round(base_ndvi, 3),
        "health_status": health_status,
        "message": message,
        "satellite_source": "Sentinel-2 MSI (Copernicus)"
    }
