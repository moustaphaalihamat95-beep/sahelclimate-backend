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

# --- Bases de données en mémoire ---
parcels_db = [
    {
        "id": 1,
        "name": "Parcelle Moussoro Est",
        "area_ha": 2.5,
        "crop_type": "Mil (Sorgho)",
        "location": "Moussoro, Barh El Gazel",
        "status": "Irrigation active"
    },
    {
        "id": 2,
        "name": "Champ Nord - Sésame",
        "area_ha": 1.2,
        "crop_type": "Sésame",
        "location": "Moussoro, Barh El Gazel",
        "status": "Sous observation"
    }
]

trainings_db = [
    {
        "id": 1,
        "title": "Techniques de Compostage Rapide au Sahel",
        "category": "Agro-écologie",
        "duration": "15 min",
        "summary": "Fabriquer un compost riche à partir de fumier local et de débris végétaux sans gaspiller d'eau."
    },
    {
        "id": 2,
        "title": "Gestion Optimisée de l'Eau de Pluie",
        "category": "Irrigation",
        "duration": "20 min",
        "summary": "Techniques de demi-lunes et zaï pour capturer l'eau et revitaliser les sols arides."
    },
    {
        "id": 3,
        "title": "Biopesticides Naturels à Base de Neem",
        "category": "Protection des Cultures",
        "duration": "10 min",
        "summary": "Préparer une solution répulsive contre les chenilles et pucerons sans produits chimiques."
    }
]

community_posts_db = [
    {
        "id": 1,
        "author": "Mahamat A.",
        "location": "Moussoro",
        "message": "Alerte : Détection de chenilles processionnaires sur le sorgho au sud du canton. Pensez au traitement bio neem !",
        "date": "Aujourd'hui"
    },
    {
        "id": 2,
        "author": "Fatimé Z.",
        "location": "Barh El Gazel",
        "message": "Les demi-lunes créées le mois dernier ont super bien retenu la dernière pluie. Très satisfaite du résultat.",
        "date": "Hier"
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
            "message": "Vent sec (Harmattan) prévu pour les prochaines 48h. Protégez les jeunes pousses de maraîchage avec des brise-vents."
        },
        {
            "id": 2,
            "type": "Irrigation",
            "severity": "Élevée",
            "message": "Forte évapotranspiration. Privilégiez l'arrosage au pied des cultures tôt le matin ou après le coucher du soleil."
        }
    ]
}

# --- Modèles Pydantic ---
class ParcelCreateRequest(BaseModel):
    name: str
    area_ha: float
    crop_type: str
    location: str

class CommunityPostRequest(BaseModel):
    author: str
    location: str
    message: str

@app.get("/")
def read_root():
    return {"message": "Tumaï Green Sahel API est opérationnelle"}

# --- Route Météo & Alertes ---
@app.get("/weather")
def get_weather():
    return weather_data

# --- Routes Parcelles ---
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
        "status": "En attente"
    }
    parcels_db.append(new_parcel)
    return {"success": True, "parcel": new_parcel}

# --- Routes Formations ---
@app.get("/trainings")
def get_trainings():
    return trainings_db

# --- Routes Communauté ---
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

# --- Routes IA ---
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
                {"role": "system", "content": "Tu es un agronome expert en cultures sahéliennes. Analyse cette image, identifie la maladie ou le problème et donne des conseils écologiques."},
                {"role": "user", "content": [{"type": "text", "text": "Diagnostic ?"}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}}]}
            ],
            max_tokens=400
        )
        return {"success": True, "diagnosis": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
