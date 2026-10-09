from pydantic import BaseModel, ConfigDict
from typing import Optional

class ParcelCreate(BaseModel):
    location_name: str
    crop_type: str
    growth_stage: str
    area_ha: float
    latitude: float
    longitude: float
    farmer_name: Optional[str] = None
    phone_number: Optional[str] = None

class ParcelResponse(ParcelCreate):
    id: int
    ndvi_value: Optional[float] = 0.65
    ndwi_value: Optional[float] = 0.42

    model_config = ConfigDict(from_attributes=True)

class WaterBalanceInput(BaseModel):
    growth_stage: str
    temp_mean: float
    temp_max: float
    temp_min: float
    humidity_mean: float
    wind_speed: float
    rain_mm: float

class AlertInput(BaseModel):
    channel: str
