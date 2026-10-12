from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import base64
from typing import Optional

app = FastAPI(title="SahelClimate API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

users_db = {}
verification_codes = {}

@app.get("/")
def read_root():
    return {"message": "SahelClimate API est opérationnelle"}

@app.post("/auth/register-phone")
async def register_phone(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}
    
    phone = str(body.get("phone_number") or body.get("phone") or "+23560000000").strip()
    name = str(body.get("full_name") or body.get("name") or "Agriculteur").strip()
    city = str(body.get("city") or "Moussoro").strip()
    address = str(body.get("address") or "Quartier Centre").strip()
    code = "123456"

    # Affichage TRÈS CLAIR dans les logs Uvicorn/Render
    print(f"\n==============================================")
    print(f"🔑 CODE SMS GENERÉ POUR {phone} : {code}")
    print(f"==============================================\n", flush=True)

    user_data = {
        "phone_number": phone,
        "full_name": name,
        "city": city,
        "address": address,
        "verified": False
    }

    verification_codes[phone] = code
    users_db[phone] = user_data

    return {
        "success": True,
        "message": f"Code de vérification généré : {code}",
        "test_code": code,
        "user": user_data
    }

@app.post("/auth/confirm-phone")
async def confirm_phone(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}

    phone = str(body.get("phone_number") or body.get("phone") or "").strip()
    
    if phone in users_db:
        users_db[phone]["verified"] = True

    return {
        "success": True,
        "message": "Compte vérifié avec succès",
        "user": users_db.get(phone, {
            "phone_number": phone,
            "full_name": "Agriculteur",
            "city": "Moussoro",
            "address": "Centre",
            "verified": True
        })
    }

@app.get("/weather")
def get_weather():
    return {
        "location": "Moussoro / Barh El Gazel",
        "temperature": "36°C",
        "humidity": "28%",
        "wind": "18 km/h (Harmattan)",
        "condition": "Ensoleillé"
    }

@app.get("/parcels")
def get_parcels():
    return [
        {"id": 1, "name": "Parcelle Moussoro Est", "area_ha": 2.5, "crop_type": "Mil (Sorgho)", "location": "Moussoro", "status": "Actif", "lat": 13.6405, "lng": 16.4901}
    ]

@app.get("/trainings")
def get_trainings():
    return [
        {"id": 1, "title": "Techniques de Compostage Rapide", "category": "Agro-écologie", "summary": "Fabriquer un compost riche sans gaspiller d'eau."}
    ]

@app.get("/community")
def get_community():
    return [
        {"id": 1, "author": "Mahamat A.", "location": "Moussoro", "message": "Alerte : Présence de chenilles sur le sorgho au sud.", "date": "Aujourd'hui"}
    ]
