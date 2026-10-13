from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SahelClimate API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "API Tumaï Green Sahel opérationnelle"}

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
    delivery_channel = str(body.get("delivery_channel") or "sms").lower()

    code = "123456"
    target_destination = phone if delivery_channel == "sms" else (email or phone)

    print(f"\n==============================================")
    print(f"🔑 CODE GENERÉ POUR {target_destination} : {code}")
    print(f"==============================================\n", flush=True)

    user_data = {
        "full_name": full_name,
        "phone_number": phone,
        "email": email,
        "city": city,
        "address": address,
        "verified": False
    }

    return {
        "success": True,
        "message": f"Code généré avec succès",
        "verification_code": code,
        "target": target_destination,
        "user": user_data
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
        {"id": 1, "author": "Mahamat A.", "location": "Moussoro", "message": "Alerte : Détection de chenilles processionnaires sur le sorgho.", "date": "Aujourd'hui"}
    ]
