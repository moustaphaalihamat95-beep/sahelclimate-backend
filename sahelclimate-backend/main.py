from fastapi import FastAPI
from app.database import engine, Base
from app.routers import parcels, alerts

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SahelClimate Backend API",
    description="API de suivi agro-climatique, calcul du bilan hydrique FAO-56 et gestion d'alertes pour le Sahel.",
    version="1.0.0"
)
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(parcels.router)
app.include_router(alerts.router)

# Integration du module d'alertes SMS/WhatsApp
from routers.alerts import router as alerts_router
app.include_router(alerts_router)

# Routeur d'exportation de rapports PDF / Excel
from routers.reports import router as reports_router
app.include_router(reports_router)
