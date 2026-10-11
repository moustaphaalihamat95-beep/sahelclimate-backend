from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random

app = FastAPI(title="SahelClimate API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Stockage temporaire en mémoire des codes de vérification (en attendant la BDD)
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
    # Génération d'un code à 4 chiffres
    code = str(random.randint(1000, 9999))
    verification_codes[data.phone] = code
    
    # Affichage du code dans les logs de Render pour test direct
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
