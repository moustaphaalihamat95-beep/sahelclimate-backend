from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
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

@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <title>Tumaï Green Sahel - Test IA</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 650px; margin: 40px auto; padding: 20px; background: #f4f7f6; color: #333; }
            .card { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            h1 { color: #1b5e20; text-align: center; }
            h2 { color: #2e7d32; font-size: 1.2rem; }
            button { background: #2e7d32; color: white; border: none; padding: 10px 15px; border-radius: 4px; cursor: pointer; font-weight: bold; }
            button:hover { background: #1b5e20; }
            pre { background: #e8f5e9; padding: 12px; border-radius: 4px; white-space: pre-wrap; font-family: inherit; margin-top: 10px; }
            input[type="file"] { margin-bottom: 10px; }
        </style>
    </head>
    <body>
        <h1>🌱 Tumaï Green Sahel</h1>
        <p style="text-align: center; color: #666;">Interface de test des modules IA (Vision & Voix)</p>
        
        <div class="card">
            <h2>1. Analyse de Plante (Diagnostic Maladie)</h2>
            <input type="file" id="plantImage" accept="image/*"><br>
            <button onclick="analyzePlant()">Analyser la photo</button>
            <pre id="plantResult">Le diagnostic de l'agronome apparaîtra ici...</pre>
        </div>

        <div class="card">
            <h2>2. Transcription Vocale (Message Agriculteur)</h2>
            <input type="file" id="audioFile" accept="audio/*"><br>
            <button onclick="transcribeAudio()">Transcrire l'audio</button>
            <pre id="audioResult">La transcription texte apparaîtra ici...</pre>
        </div>

        <script>
            async function analyzePlant() {
                const fileInput = document.getElementById('plantImage');
                if(fileInput.files.length === 0) { alert('Veuillez choisir une photo de plante'); return; }
                const formData = new FormData();
                formData.append('file', fileInput.files[0]);
                
                document.getElementById('plantResult').innerText = "Analyse en cours par GPT-4o...";
                try {
                    const res = await fetch('/ai/analyze-plant-image', { method: 'POST', body: formData });
                    const data = await res.json();
                    document.getElementById('plantResult').innerText = data.diagnosis || JSON.stringify(data, null, 2);
                } catch(err) {
                    document.getElementById('plantResult').innerText = "Erreur : " + err;
                }
            }

            async function transcribeAudio() {
                const fileInput = document.getElementById('audioFile');
                if(fileInput.files.length === 0) { alert('Veuillez choisir un fichier audio'); return; }
                const formData = new FormData();
                formData.append('file', fileInput.files[0]);
                
                document.getElementById('audioResult').innerText = "Transcription en cours par Whisper...";
                try {
                    const res = await fetch('/ai/voice-to-text', { method: 'POST', body: formData });
                    const data = await res.json();
                    document.getElementById('audioResult').innerText = data.text || JSON.stringify(data, null, 2);
                } catch(err) {
                    document.getElementById('audioResult').innerText = "Erreur : " + err;
                }
            }
        </script>
    </body>
    </html>
    """

@app.post("/auth/register-phone")
def register_phone(data: PhoneRegisterRequest):
    code = str(random.randint(1000, 9999))
    verification_codes[data.phone] = code
    print(f"\n[SMS SIMULÉ] Numéro: {data.phone} - CODE: {code}\n")
    return {"message": "Code généré", "phone": data.phone}

@app.post("/auth/confirm-phone")
def confirm_phone(data: PhoneConfirmRequest):
    if verification_codes.get(data.phone) != data.confirmation_code:
        raise HTTPException(status_code=400, detail="Code incorrect")
    return {"success": True}

@app.post("/auth/login-phone")
def login_phone(data: PhoneLoginRequest):
    return {"access_token": "fake-token"}

@app.get("/parcels")
def get_parcels(): return []

@app.get("/trainings")
def get_trainings(): return []

@app.get("/community")
def get_community(): return []

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
