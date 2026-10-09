import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL PostgreSQL / PostGIS (modifiable via variable d'environnement)
POSTGIS_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://sahel_user:sahel_password@localhost:5432/sahelclimate_db"
)

# Utilisation de SQLite spatialite en secours local si PostGIS n'est pas actif
if POSTGIS_URL.startswith("sqlite"):
    engine = create_engine(POSTGIS_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(POSTGIS_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
