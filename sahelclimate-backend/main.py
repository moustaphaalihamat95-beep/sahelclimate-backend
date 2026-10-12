from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import os
import base64
from typing import List, Optional
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

# --- Modèles Pydantic flexibles ---
class PhoneRegisterRequest(BaseModel):
    phone_number: str
    full_name: str

class PhoneConfirmRequest(BaseModel):
    phone_number: str
    code: str

class PhoneLoginRequest(BaseModel):
    phone_number: str

class ParcelCreateRequest(BaseModel):
    name: str
    area_ha: float
    crop_type: str
    location: str
    lat: Optional[float] = 13.6405
    lng: Optional[float] = 16.4901

class CommunityPostRequest(BaseModel):
    author: str
    location: str
    message: str

@app.get("/")
def read_root():
    return {"message": "Tumaï Green Sahel API est opérationnelle"}

# --- Routes Auth ---
@app.post("/auth/register-phone")
def register_phone(req: PhoneRegisterRequest):
    phone = req.phone_number.strip()
    name = req.full_name.strip()
    code = "123456"
    verification_codes[phone] = code
    users_db[phone] = {"phone_number": phone, "full_name": name, "verified": False}
    return {"success": True, "message": f"Code envoyé au {phone}", "test_code": code}

@app.post("/auth/confirm-phone")
def confirm_phone(req: PhoneConfirmRequest):
    phone = req.phone_number.strip()
    code = req.code.strip()
    saved_code = verification_codes.get(phone)
    if saved_code and saved_code == code:
        if phone in users_db:
            users_db[phone]["verified"] = True
        return {"success": True, "message": "Vérifié avec succès", "user": users_db.get(phone)}
    raise HTTPException(status_code=400, detail="Code invalide")

@app.post("/auth/login-phone")
def login_phone(req: PhoneLoginRequest):
    phone = req.phone_number.strip()
    if phone in users_db:
        code = "123456"
        verification_codes[phone] = code
        return {"success": True, "message": "Code envoyé", "test_code": code}
    # Auto-création pour éviter le blocage si non inscrit
    users_db[phone] = {"phone_number": phone, "full_name": "Agriculteur Sahel", "verified": True}
    return {"success": True, "message": "Numéro reconnu, code envoyé", "test_code": "123456"}

# --- Routes Générales ---
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
    return {"success": True, "text": "Transcription simulée (en attente de crédits OpenAI)"}

@app.post("/ai/analyze-plant-image")
async def analyze_plant_image(file: UploadFile = File(...)):
    return {"success": True, "diagnosis": "Diagnostic simulé : Plante en bonne santé apparente. Maintenez une bonne hydratation."}
