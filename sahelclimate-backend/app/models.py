from sqlalchemy import Column, Integer, String, Float
from app.database import Base

class ParcelModel(Base):
    __tablename__ = "parcels"

    id = Column(Integer, primary_key=True, index=True)
    location_name = Column(String, index=True)
    crop_type = Column(String)
    growth_stage = Column(String)
    area_ha = Column(Float)
    latitude = Column(Float)
    longitude = Column(Float)
    farmer_name = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
