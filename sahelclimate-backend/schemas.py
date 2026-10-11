from pydantic import BaseModel, Field
from typing import Optional

class ParcelCreate(BaseModel):
    name: str
    crop_type: str = "Maïs"
    area_ha: float = 1.0
    latitude: float = 12.1348
    longitude: float = 15.0557
    soil_type: Optional[str] = "Sableux"  # Optionnel pour éviter l'erreur 422 si absent
    planting_date: Optional[str] = "2026-06-01"  # Optionnel
