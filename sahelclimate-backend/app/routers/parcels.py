from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import ParcelModel
from app.schemas import ParcelCreate, ParcelResponse, WaterBalanceInput
from app.services.satellite import SentinelService
from app.services.weather import WeatherService

router = APIRouter(prefix="/api/v1/parcels", tags=["Parcels, Satellite & Weather"])

@router.get("", response_model=List[ParcelResponse], summary="Get Parcels")
def get_parcels(db: Session = Depends(get_db)):
    parcels = db.query(ParcelModel).all()

    if not parcels:
        default_parcel = ParcelModel(
            location_name="Parcelle Demo Sahel",
            crop_type="Sésame",
            growth_stage="dev",
            area_ha=2.5,
            latitude=12.11,
            longitude=15.05
        )
        db.add(default_parcel)
        db.commit()
        db.refresh(default_parcel)
        parcels = [default_parcel]

    result = []
    for p in parcels:
        satellite_data = SentinelService.get_parcel_indices(p.latitude, p.longitude)
        data = ParcelResponse.model_validate(p)
        data.ndvi_value = satellite_data["ndvi_value"]
        data.ndwi_value = satellite_data["ndwi_value"]
        result.append(data)
    return result

@router.post("", response_model=ParcelResponse, summary="Create Parcel")
def create_parcel(parcel: ParcelCreate, db: Session = Depends(get_db)):
    db_parcel = ParcelModel(**parcel.model_dump())
    db.add(db_parcel)
    db.commit()
    db.refresh(db_parcel)

    satellite_data = SentinelService.get_parcel_indices(db_parcel.latitude, db_parcel.longitude)
    response_data = ParcelResponse.model_validate(db_parcel)
    response_data.ndvi_value = satellite_data["ndvi_value"]
    response_data.ndwi_value = satellite_data["ndwi_value"]
    return response_data

@router.get("/{parcel_id}/satellite-analysis", summary="Get Satellite Imagery Analysis")
def get_satellite_analysis(parcel_id: int, db: Session = Depends(get_db)):
    parcel = db.query(ParcelModel).filter(ParcelModel.id == parcel_id).first()
    if not parcel:
        raise HTTPException(status_code=404, detail="Parcelle non trouvée")

    satellite_data = SentinelService.get_parcel_indices(parcel.latitude, parcel.longitude)
    return {
        "parcel_id": parcel_id,
        "location_name": parcel.location_name,
        "coordinates": {"latitude": parcel.latitude, "longitude": parcel.longitude},
        "sentinel_analysis": satellite_data
    }

@router.get("/{parcel_id}/weather", summary="Get Current Weather Data")
def get_parcel_weather(parcel_id: int, db: Session = Depends(get_db)):
    """
    Récupère la météo en temps réel sur la parcelle via Open-Meteo.
    """
    parcel = db.query(ParcelModel).filter(ParcelModel.id == parcel_id).first()
    if not parcel:
        raise HTTPException(status_code=404, detail="Parcelle non trouvée")

    weather_data = WeatherService.get_current_weather(parcel.latitude, parcel.longitude)
    return {
        "parcel_id": parcel_id,
        "location_name": parcel.location_name,
        "coordinates": {"latitude": parcel.latitude, "longitude": parcel.longitude},
        "weather": weather_data
    }

@router.post("/{parcel_id}/auto-water-balance", summary="Calculate Automatic Water Balance via Live Weather")
def calculate_auto_water_balance(parcel_id: int, db: Session = Depends(get_db)):
    """
    Récupère la météo automatiquement et calcule le bilan hydrique FAO-56.
    """
    parcel = db.query(ParcelModel).filter(ParcelModel.id == parcel_id).first()
    if not parcel:
        raise HTTPException(status_code=404, detail="Parcelle non trouvée")

    weather = WeatherService.get_current_weather(parcel.latitude, parcel.longitude)
    
    temp_mean = weather["temp_mean"]
    temp_max = weather["temp_max"]
    temp_min = weather["temp_min"]
    rain_mm = weather["rain_mm"]

    eto = 0.0023 * (temp_mean + 17.8) * (max(0.1, temp_max - temp_min) ** 0.5) * 15.0
    kc = 0.7 if parcel.growth_stage == "dev" else 1.05
    etc = eto * kc
    deficit_mm = max(0, etc - rain_mm)
    area_ha = parcel.area_ha or 1.0
    total_volume_m3 = round(deficit_mm * 10 * area_ha, 2)

    return {
        "parcel_id": parcel_id,
        "crop_type": parcel.crop_type,
        "growth_stage": parcel.growth_stage,
        "weather_data": weather,
        "water_balance_analysis": {
            "et0_daily_mm": round(eto, 2),
            "etc_mm_day": round(etc, 2),
            "water_deficit_mm": round(deficit_mm, 2),
            "total_parcel_volume_m3": total_volume_m3,
            "status": "Optimal" if rain_mm >= etc else "Irrigation requise"
        }
    }

@router.post("/{parcel_id}/water-balance", summary="Calculate Water Balance")
def calculate_water_balance(parcel_id: int, data: WaterBalanceInput, db: Session = Depends(get_db)):
    parcel = db.query(ParcelModel).filter(ParcelModel.id == parcel_id).first()
    if not parcel:
        raise HTTPException(status_code=404, detail="Parcelle non trouvée")

    eto = 0.0023 * (data.temp_mean + 17.8) * ((data.temp_max - data.temp_min) ** 0.5) * 15.0
    kc = 0.7 if data.growth_stage == "dev" else 1.05
    etc = eto * kc
    deficit_mm = max(0, etc - data.rain_mm)
    area_ha = parcel.area_ha or 1.0
    total_volume_m3 = round(deficit_mm * 10 * area_ha, 2)

    return {
        "parcel_id": parcel_id,
        "water_balance_analysis": {
            "et0_daily_mm": round(eto, 2),
            "eto_mm_day": round(eto, 2),
            "etc_mm_day": round(etc, 2),
            "water_deficit_mm": round(deficit_mm, 2),
            "total_parcel_volume_m3": total_volume_m3,
            "status": "Optimal" if data.rain_mm >= etc else "Irrigation requise"
        }
    }
