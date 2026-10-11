from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["Authentication"])

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

@router.post("/register-phone")
def register_phone(data: PhoneRegisterRequest):
    # Logique d'inscription par téléphone et envoi SMS
    return {"message": "Code de confirmation envoyé par SMS", "phone": data.phone}

@router.post("/confirm-phone")
def confirm_phone(data: PhoneConfirmRequest):
    # Logique de validation du code SMS
    return {"message": "Téléphone vérifié avec succès"}

@router.post("/login-phone")
def login_phone(data: PhoneLoginRequest):
    # Logique de connexion par téléphone
    return {"access_token": "fake-token", "token_type": "bearer"}
