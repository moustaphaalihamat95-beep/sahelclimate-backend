from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random
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

# --- Infos Développeur ---
developer_info = {
    "name": "Moustapha Ali hamat",
    "role": "Développeur Full-Stack & Ingénieur Solutions Sahéliennes",
    "email": "moustapha.ali.hamat@example.com",
    "phone": "+23560646072",
    "whatsapp": "+23560646072",
    "location": "N'Djamena / Moussoro, Tchad"
}

# --- DB en mémoire ---
feedbacks_db = []
user_profile_db = {
    "full_name": "Moustapha Ali hamat",
    "email": "moustapha.ali.hamat@example.com",
    "phone": "+23560646072",
    "city": "Moussoro",
    "province": "Barh El Gazel",
    "avatar_url": ""
}
users_db = {}

# --- Modèles ---
class FeedbackRequest(BaseModel):
    user_name: str
    contact: str
    subject: str
    message: str

class ProfileUpdateRequest(BaseModel):
    full_name: str
    email: Optional[str] = ""
    phone: str
    city: str
    province: Optional[str] = ""

class PhoneRegisterRequest(BaseModel):
    full_name: Optional[str] = ""
    phone: str
    password: Optional[str] = ""

class PhoneConfirmRequest(BaseModel):
    phone: str
    code: str

class PhoneLoginRequest(BaseModel):
    phone: str
    password: Optional[str] = ""

# --- Routes Contact & Support ---
@app.get("/developer")
def get_developer_info():
    return developer_info

@app.post("/feedback")
def send_feedback(req: FeedbackRequest):
    new_feedback = {
        "id": len(feedbacks_db) + 1,
        "user_name": req.user_name,
        "contact": req.contact,
        "subject": req.subject,
        "message": req.message
    }
    feedbacks_db.append(new_feedback)
    return {"success": True, "message": "Votre message a bien été envoyé au développeur !"}

# --- Routes Auth & Profil ---
@app.get("/profile")
def get_profile():
    return user_profile_db

@app.post("/profile")
def update_profile(req: ProfileUpdateRequest):
    user_profile_db["full_name"] = req.full_name
    user_profile_db["email"] = req.email
    user_profile_db["phone"] = req.phone
    user_profile_db["city"] = req.city
    user_profile_db["province"] = req.province
    return {"success": True, "profile": user_profile_db}

@app.post("/profile/avatar")
async def upload_avatar(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        encoded = base64.b64encode(contents).decode("utf-8")
        mime_type = file.content_type or "image/jpeg"
        avatar_url = f"data:{mime_type};base64,{encoded}"
        user_profile_db["avatar_url"] = avatar_url
        return {"success": True, "avatar_url": avatar_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/auth/register-phone")
def register_phone(req: PhoneRegisterRequest):
    users_db[req.phone] = {
        "full_name": req.full_name,
        "phone": req.phone,
        "password": req.password,
        "verified": True
    }
    user_profile_db["full_name"] = req.full_name or user_profile_db["full_name"]
    user_profile_db["phone"] = req.phone
    return {"success": True, "message": "Compte créé avec succès !"}

@app.post("/auth/confirm-phone")
def confirm_phone(req: PhoneConfirmRequest):
    return {"success": True, "message": "Numéro confirmé avec succès !"}

@app.post("/auth/login-phone")
def login_phone(req: PhoneLoginRequest):
    return {"success": True, "user": user_profile_db}

# --- Rest of endpoints ---
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
        "summary": "Fabriquer un compost riche sans gaspiller d'eau."
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
            "message": "Vent sec (Harmattan) prévu pour les prochaines 48h."
        }
    ]
}

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
    return {"message": "SahelClimate API est opérationnelle"}

@app.get("/weather")
def get_weather():
    return weather_data

@app.get("/parcels")
def get_parcels():
    return parcels_db

@app.post("/parcels")
def create_parcel(parcel: ParcelCreateRequest):
    new_parcel = {
        "id": len(parcels_db) + 1,
        "name": parcel.name,
        "area_ha": parcel.area_ha,
        "crop_type": parcel.crop_type,
        "location": parcel.location,
        "status": "En attente",
        "lat": parcel.lat or 13.6405,
        "lng": parcel.lng or 16.4901
    }
    parcels_db.append(new_parcel)
    return {"success": True, "parcel": new_parcel}

@app.get("/trainings")
def get_trainings():
    return trainings_db

@app.get("/community")
def get_community():
    return community_posts_db

@app.post("/community")
def create_community_post(post: CommunityPostRequest):
    new_post = {
        "id": len(community_posts_db) + 1,
        "author": post.author,
        "location": post.location,
        "message": post.message,
        "date": "À l'instant"
    }
    community_posts_db.insert(0, new_post)
    return {"success": True, "post": new_post}

@app.post("/ai/voice-to-text")
async def voice_to_text(file: UploadFile = File(...)):
    temp_audio_path = f"temp_{file.filename}"
    try:
        with open(temp_audio_path, "wb") as buffer:
            buffer.write(await file.read())
        with open(temp_audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file, language="fr")
        os.remove(temp_audio_path)
        return {"success": True, "text": transcript.text}
    except Exception as e:
        if os.path.exists(temp_audio_path): os.remove(temp_audio_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/analyze-plant-image")
async def analyze_plant_image(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        encoded_image = base64.b64encode(image_bytes).decode("utf-8")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Tu es un agronome expert en cultures sahéliennes. Analyse cette image."},
                {"role": "user", "content": [{"type": "text", "text": "Diagnostic ?"}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}}]}
            ],
            max_tokens=400
        )
        return {"success": True, "diagnosis": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
