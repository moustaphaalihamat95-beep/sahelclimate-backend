from pydantic import BaseModel, Field
from typing import List, Optional

class Coordinate(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)

class ParcelAnalysisRequest(BaseModel):
    parcel_id: str
    farmer_id: str
    coordinates: List[Coordinate]
    start_date: Optional[str] = "2026-08-01"
    end_date: Optional[str] = "2026-09-01"

class NDVIAnalysisResponse(BaseModel):
    parcel_id: str
    mean_ndvi: float
    status: str
    drought_risk_detected: bool
    trigger_payout: bool
    recommended_action: str
