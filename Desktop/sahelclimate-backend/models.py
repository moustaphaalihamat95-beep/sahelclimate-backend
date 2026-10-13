from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from datetime import datetime
from database import Base

class Parcel(Base):
    __tablename__ = "parcels"

    id = Column(Integer, primary_key=True, index=True)
    owner_name = Column(String, default="Producteur Anonyme")
    location_name = Column(String, default="Moussoro")
    area_ha = Column(Float)
    ndvi_value = Column(Float)
    geojson_geometry = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
