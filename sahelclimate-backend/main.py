from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="SahelClimate API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    return {"message": "Code de confirmation envoyé par SMS", "phone": data.phone}

@app.post("/auth/confirm-phone")
def confirm_phone(data: PhoneConfirmRequest):
    return {"message": "Téléphone vérifié avec succès"}

@app.post("/auth/login-phone")
def login_phone(data: PhoneLoginRequest):
    return {"access_token": "fake-token", "token_type": "bearer"}
