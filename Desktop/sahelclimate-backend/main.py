from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random
import os
from twilio.rest import Client

app = FastAPI(title="SahelClimate-AI API", version="2.0")

# Autoriser les requêtes depuis le frontend Netlify
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration Twilio (récupérée depuis les variables d'environnement sur Render)
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

def send_real_sms(phone_number: str, code: str) -> bool:
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN or not TWILIO_PHONE_NUMBER:
        print("⚠️ Twilio non configuré dans les variables d'environnement. Mode simulation actif.")
        return False

    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=f"Votre code d'activation SahelClimate-AI est : {code}",
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        print(f"✅ SMS envoyé avec succès à {phone_number}. SID: {message.sid}")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi du SMS via Twilio: {e}")
        return False

class UserRegister(BaseModel):
    full_name: str
    phone_number: str
    city: str
    address: str = ""
    email: str = ""
    password: str
    delivery_channel: str = "sms"

class ParcelCreate(BaseModel):
    location_name: str
    crop_type: str
    area_ha: float
    ndvi_value: float = 0.45

# Base de données temporaire en mémoire
parcels_db = [
    {"id": 1, "location_name": "Parcelle N'Djamena Nord", "area_ha": 15.2, "crop_type": "Maïs", "ndvi_value": 0.52},
    {"id": 2, "location_name": "Zone Bahr El Gazel", "area_ha": 8.7, "crop_type": "Sorgho", "ndvi_value": 0.38}
]

@app.get("/")
def read_root():
    return {"status": "online", "system": "SahelClimate-AI Backend v2.0"}

@app.post("/auth/register")
def register(user: UserRegister):
    # Génération d'un code unique à 6 chiffres
    verification_code = str(random.randint(100000, 999999))
    
    # Envoi du SMS réel
    sms_success = False
    if user.delivery_channel == "sms" and user.phone_number:
        sms_success = send_real_sms(user.phone_number, verification_code)

    return {
        "status": "success",
        "message": "Inscription enregistrée",
        "sms_sent": sms_success,
        "verification_code": verification_code  # Conservé pour la démo/validation locale
    }

@app.get("/api/v1/parcels")
def get_parcels():
    return parcels_db

@app.post("/api/v1/parcels")
def create_parcel(parcel: ParcelCreate):
    new_id = len(parcels_db) + 1
    new_parcel = {
        "id": new_id,
        "location_name": parcel.location_name,
        "area_ha": parcel.area_ha,
        "crop_type": parcel.crop_type,
        "ndvi_value": parcel.ndvi_value
    }
    parcels_db.append(new_parcel)
    return new_parcel

@app.get("/api/v1/parcels/{parcel_id}/diagnostic")
def get_diagnostic(parcel_id: int):
    parcel = next((p for p in parcels_db if p["id"] == parcel_id), None)
    if not parcel:
        raise HTTPException(status_code=404, detail="Parcelle non trouvée")
    
    ndvi = parcel["ndvi_value"]
    health = "Végétation Vigoureuse" if ndvi >= 0.5 else "Stress Hydrique Modéré"
    risk = "Faible" if ndvi >= 0.5 else "Moyen"
    rec = "Maintenir l'arrosage régulier (10-12 mm/semaine)" if ndvi >= 0.5 else "Augmenter la fréquence d'irrigation (18-20 mm/semaine)"

    return {
        "parcel_id": parcel["id"],
        "location_name": parcel["location_name"],
        "crop_type": parcel["crop_type"],
        "area_ha": parcel["area_ha"],
        "ndvi_value": ndvi,
        "health_status": health,
        "drought_risk": risk,
        "irrigation_recommendation": rec
    }
