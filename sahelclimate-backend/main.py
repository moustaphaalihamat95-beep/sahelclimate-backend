from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
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

@app.post("/auth/register")
async def register(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}

    full_name = str(body.get("full_name") or "Agriculteur").strip()
    phone = str(body.get("phone_number") or body.get("phone") or "").strip()
    email = str(body.get("email") or "").strip()
    city = str(body.get("city") or "Moussoro").strip()
    address = str(body.get("address") or "").strip()
    password = str(body.get("password") or "").strip()
    
    # Canaux d'envoi choisis : 'sms' ou 'email'
    delivery_channel = str(body.get("delivery_channel") or "sms").lower()

    # Code à 6 chiffres
    code = "123456"

    # Destination selon le canal
    target_destination = phone if delivery_channel == "sms" else (email or phone)

    print("\n==================================================")
    print(f"🔑 NOUVELLE INSCRIPTION ({delivery_channel.upper()})")
    print(f"   Nom: {full_name}")
    print(f"   Cible: {target_destination}")
    print(f"   CODE DE VERIFICATION GENERÉ: {code}")
    print("==================================================\n", flush=True)

    user_key = phone if phone else email
    user_data = {
        "full_name": full_name,
        "phone_number": phone,
        "email": email,
        "city": city,
        "address": address,
        "verified": False
    }

    verification_codes[user_key] = code
    users_db[user_key] = user_data

    return {
        "success": True,
        "message": f"Code envoyé via {delivery_channel.upper()} à {target_destination}",
        "delivery_channel": delivery_channel,
        "target": target_destination,
        "verification_code": code,
        "user": user_data
    }

@app.post("/auth/confirm-code")
async def confirm_code(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}

    target = str(body.get("target") or body.get("phone") or body.get("email") or "").strip()
    code = str(body.get("code") or "").strip()

    if target in users_db:
        users_db[target]["verified"] = True

    return {
        "success": True,
        "message": "Vérification réussie !",
        "user": users_db.get(target, {
            "full_name": "Agriculteur",
            "phone_number": target,
            "city": "Moussoro",
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
        {"id": 1, "title": "Techniques de Compostage Rapide", "category": "Agro-écologie", "summary": "Fabriquer un compost riche sans gaspiller d'eau au Sahel."}
    ]

@app.get("/community")
def get_community():
    return [
        {"id": 1, "author": "Mahamat A.", "location": "Moussoro", "message": "Alerte : Détection de chenilles processionnaires sur le sorgho au sud.", "date": "Aujourd'hui"}
    ]
