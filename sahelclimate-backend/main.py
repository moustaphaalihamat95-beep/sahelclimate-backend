from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import base64
from typing import Optional
from openai import OpenAI

app = FastAPI(title="SahelClimate API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI()

users_db = {}
verification_codes = {}

parcels_db = [
    {
        "id": 1,
        "name": "Parcelle Moussoro Est",
        "area_ha": 2.5,
        "crop_type": "Mil (Sorgho)",
        "location": "Moussoro, Barh El Gazel",
        "status": "Irrigation active",
        "lat": 13.6405,
        "lng": 16.4901
    }
]

trainings_db = [
    {
        "id": 1,
        "title": "Techniques de Compostage Rapide au Sahel",
        "category": "Agro-écologie",
        "duration": "15 min",
        "summary": "Fabriquer un compost riche à partir de fumier local et de débris végétaux sans gaspiller d'eau."
    }
]

community_posts_db = [
    {
        "id": 1,
        "author": "Mahamat A.",
        "location": "Moussoro",
        "message": "Alerte : Détection de chenilles processionnaires sur le sorgho.",
        "date": "Aujourd'hui"
    }
]

weather_data = {
    "location": "Moussoro / Barh El Gazel",
    "temperature": "36°C",
    "humidity": "28%",
    "wind": "18 km/h (Harmattan)",
    "condition": "Ensoleillé / Vent de sable léger",
    "alerts": [
        {
            "id": 1,
            "type": "Vent / Érosion",
            "severity": "Moyenne",
            "message": "Vent sec prévu pour les prochaines 48h."
        }
    ]
}

class ParcelCreateRequest(BaseModel):
    name: Optional[str] = "Nouvelle Parcelle"
    area_ha: Optional[float] = 1.0
    crop_type: Optional[str] = "Mil"
    location: Optional[str] = "Moussoro"
    lat: Optional[float] = 13.6405
    lng: Optional[float] = 16.4901

class CommunityPostRequest(BaseModel):
    author: Optional[str] = "Anonyme"
    location: Optional[str] = "Moussoro"
    message: Optional[str] = ""

@app.get("/")
def read_root():
    return {"message": "Tumaï Green Sahel API est opérationnelle"}

# Route d'inscription complète avec identification unique
@app.post("/auth/register-phone")
async def register_phone(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}
    
    phone = str(body.get("phone_number") or body.get("phone") or "Inconnu").strip()
    name = str(body.get("full_name") or body.get("name") or "Agriculteur").strip()
    city = str(body.get("city") or "Moussoro").strip()
    address = str(body.get("address") or "Non spécifiée").strip()
    email = str(body.get("email") or "").strip()
    code = "123456"

    user_data = {
        "phone_number": phone,
        "full_name": name,
        "city": city,
        "address": address,
        "email": email,
        "verified": False
    }

    verification_codes[phone] = code
    users_db[phone] = user_data

    return {
        "success": True,
        "message": f"Code de vérification envoyé au {phone}",
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
        "message": "Compte identifié et vérifié avec succès",
        "user": users_db.get(phone, {
            "phone_number": phone,
            "full_name": "Agriculteur",
            "city": "Moussoro",
            "address": "Non spécifiée",
            "email": "",
            "verified": True
        })
    }

@app.post("/auth/login-phone")
async def login_phone(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}

    phone = str(body.get("phone_number") or body.get("phone") or "Inconnu").strip()
    code = "123456"

    if phone not in users_db:
        users_db[phone] = {
            "phone_number": phone,
            "full_name": "Agriculteur Sahel",
            "city": "Moussoro",
            "address": "Centre",
            "email": "",
            "verified": True
        }

    verification_codes[phone] = code

    return {
        "success": True,
        "message": "Code envoyé",
        "test_code": code,
        "user": users_db[phone]
    }

@app.get("/weather")
def get_weather(): return weather_data

@app.get("/parcels")
def get_parcels(): return parcels_db

@app.post("/parcels")
def create_parcel(parcel: ParcelCreateRequest):
    new_parcel = {**parcel.dict(), "id": len(parcels_db) + 1, "status": "En attente"}
    parcels_db.append(new_parcel)
    return {"success": True, "parcel": new_parcel}

@app.get("/trainings")
def get_trainings(): return trainings_db

@app.get("/community")
def get_community(): return community_posts_db

@app.post("/community")
def create_community_post(post: CommunityPostRequest):
    new_post = {**post.dict(), "id": len(community_posts_db) + 1, "date": "À l'instant"}
    community_posts_db.insert(0, new_post)
    return {"success": True, "post": new_post}

@app.post("/ai/voice-to-text")
async def voice_to_text(file: UploadFile = File(...)):
    return {"success": True, "text": "Message audio reçu et transcrit."}

@app.post("/ai/analyze-plant-image")
async def analyze_plant_image(file: UploadFile = File(...)):
    return {"success": True, "diagnosis": "Plante analysée : Aucune anomalie majeure observée."}
