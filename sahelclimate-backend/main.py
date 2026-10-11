from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random
import os
import base64
from openai import OpenAI

app = FastAPI(title="SahelClimate API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialisation du client OpenAI (nécessite la variable d'environnement OPENAI_API_KEY sur Render)
client = OpenAI()

verification_codes = {}

class PhoneRegisterRequest(BaseModel):
    name: str
    phone: str
    password: str

class PhoneConfirmRequest(BaseModel):
    phone: str
    confirmation_code: str

class PhoneLoginRequest(BaseModel):
    phone: str
    password: str

@app.get("/")
def read_root():
    return {"status": "Backend SahelClimate opérationnel"}

@app.post("/auth/register-phone")
def register_phone(data: PhoneRegisterRequest):
    code = str(random.randint(1000, 9999))
    verification_codes[data.phone] = code
    print(f"\n========================================")
    print(f" [SMS SIMULÉ] Numéro: {data.phone}")
    print(f" [SMS SIMULÉ] CODE DE CONFIRMATION: {code}")
    print(f"========================================\n")
    return {"message": "Code de confirmation généré", "phone": data.phone}

@app.post("/auth/confirm-phone")
def confirm_phone(data: PhoneConfirmRequest):
    stored_code = verification_codes.get(data.phone)
    if not stored_code or stored_code != data.confirmation_code:
        raise HTTPException(status_code=400, detail="Code de confirmation incorrect")
    return {"message": "Téléphone vérifié avec succès", "success": True}

@app.post("/auth/login-phone")
def login_phone(data: PhoneLoginRequest):
    return {"access_token": "fake-token-sahel", "token_type": "bearer"}

@app.get("/parcels")
def get_parcels():
    return []

@app.get("/trainings")
def get_trainings():
    return []

@app.get("/community")
def get_community():
    return []

# --- NOUVEAUX MODULES IA ---

@app.post("/ai/voice-to-text")
async def voice_to_text(file: UploadFile = File(...)):
    """Convertit un message vocal d'agriculteur en texte via Whisper."""
    temp_audio_path = f"temp_{file.filename}"
    try:
        with open(temp_audio_path, "wb") as buffer:
            buffer.write(await file.read())

        with open(temp_audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="fr"
            )

        os.remove(temp_audio_path)
        return {"success": True, "text": transcript.text}

    except Exception as e:
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
        raise HTTPException(status_code=500, detail=f"Erreur transcription vocale : {str(e)}")

@app.post("/ai/analyze-plant-image")
async def analyze_plant_image(file: UploadFile = File(...)):
    """Analyse une photo de culture pour diagnostiquer une maladie (GPT-4o)."""
    try:
        image_bytes = await file.read()
        encoded_image = base64.b64encode(image_bytes).decode("utf-8")

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Tu es un agronome expert en cultures sahéliennes. Analyse cette image de plante, identifie la maladie ou le problème nutritionnel, et donne des conseils de traitement écologiques et pratiques adaptés au Sahel."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Quel est le problème sur cette culture et comment le soigner ?"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{encoded_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500
        )

        return {"success": True, "diagnosis": response.choices[0].message.content}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur d'analyse d'image : {str(e)}")
