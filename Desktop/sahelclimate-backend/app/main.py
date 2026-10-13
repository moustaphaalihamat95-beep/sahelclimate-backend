from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="SahelClimate-AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Parcel(BaseModel):
    id: Optional[int] = None
    location_name: str
    area_ha: float
    crop_type: Optional[str] = "Maïs"
    ndvi_value: Optional[float] = 0.45

db_parcels = [
    {"id": 1, "location_name": "Parcelle N'Djamena Nord", "area_ha": 15.2, "crop_type": "Maïs", "ndvi_value": 0.52},
    {"id": 2, "location_name": "Zone Bahr El Gazel", "area_ha": 8.7, "crop_type": "Sorgho", "ndvi_value": 0.38},
]

@app.get("/")
def root():
    return {"status": "SahelClimate-AI API opérationnelle"}

@app.get("/api/v1/parcels", response_model=List[Parcel])
def get_parcels():
    return db_parcels
