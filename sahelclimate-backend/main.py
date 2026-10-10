from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import io
import csv

app = FastAPI(title="SahelClimate-AI API", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API SahelClimate-AI", "version": "1.1.0"}

# --- BASE DE DONNÉES EN MÉMOIRE ---

fake_users_db = []
pending_confirmations_db = {}

# Parcelles incluant le Sahel (Nord/Centre) et la Zone Soudanienne (Sud-Ouest)
fake_parcels_db = [
    {
        "id": 1,
        "name": "Parcelle N'Djamena Nord",
        "latitude": 12.1348,
        "longitude": 15.0557,
        "crop_type": "Maïs",
        "area_ha": 2.5,
        "zone": "Sahel"
    },
    {
        "id": 2,
        "name": "Parcelle Moussoro Sud",
        "latitude": 13.6406,
        "longitude": 16.4901,
        "crop_type": "Sorgho",
        "area_ha": 4.0,
        "zone": "Sahel"
    },
    {
        "id": 3,
        "name": "Exploitation Cotonnière Moundou",
        "latitude": 8.5667,
        "longitude": 16.0833,
        "crop_type": "Coton",
        "area_ha": 5.0,
        "zone": "Sud-Ouest"
    },
    {
        "id": 4,
        "name": "Champs de Manioc Doba",
        "latitude": 8.6500,
        "longitude": 16.8500,
        "crop_type": "Manioc",
        "area_ha": 3.2,
        "zone": "Sud-Ouest"
    },
    {
        "id": 5,
        "name": "Bassin d'Arachide & Sésame Pala",
        "latitude": 9.3642,
        "longitude": 14.9047,
        "crop_type": "Arachide",
        "area_ha": 1.8,
        "zone": "Sud-Ouest"
    }
]

fake_trainings_db = [
    {
        "id": 1,
        "title": "Technique du Zaï et Récupération des Sols Dégradés",
        "category": "Agriculture Régénératrice (Sahel)",
        "description": "Apprenez à creuser des poquets pour concentrer l'eau de pluie et le compost dans les zones arides.",
        "duration": "15 min"
    },
    {
        "id": 2,
        "title": "Agroforesterie du Karité et du Néré",
        "category": "Conservation & Valorisation (Sud-Ouest)",
        "description": "Protection des parcs à karité, taille de régénération et récolte durable des noix et graines.",
        "duration": "20 min"
    },
    {
        "id": 3,
        "title": "Lutte Intégrée contre les Chenilles du Coton",
        "category": "Protection des Cultures",
        "description": "Bonnes pratiques de rotation des cultures et traitements biologiques adaptés à la zone cotonnivore.",
        "duration": "12 min"
    }
]

fake_community_posts = [
    {
        "id": 1,
        "author": "Moussa (N'Djamena)",
        "message": "Le reboisement d'Acacia senegal en bordure a nettement réduit l'impact des vents de sable.",
        "date": "Il y a 2 jours"
    },
    {
        "id": 2,
        "author": "Célestin (Moundou)",
        "message": "L'association manioc et arachide donne de très bons résultats d'humidité dans le Logone Occidental cette saison.",
        "date": "Hier"
    }
]

# --- SCHÉMAS PYDANTIC ---

class PhoneRegister(BaseModel):
    name: str
    phone: str
    password: str

class PhoneConfirm(BaseModel):
    phone: str
    confirmation_code: str

class PhoneLogin(BaseModel):
    phone: str
    password: str

class ParcelCreate(BaseModel):
    name: str
    crop_type: Optional[str] = "Maïs"
    area_ha: Optional[float] = 1.0
    latitude: Optional[float] = 12.1348
    longitude: Optional[float] = 15.0557

class PostCreate(BaseModel):
    author: str
    message: str

# --- ROUTES D'AUTHENTIFICATION ---

@app.post("/api/v1/auth/register-phone")
def register_phone(user: PhoneRegister):
    code = "123456"
    pending_confirmations_db[user.phone] = {
        "name": user.name,
        "phone": user.phone,
        "password": user.password,
        "code": code
    }
    return {
        "message": f"Code de confirmation envoyé par SMS au {user.phone}",
        "demo_code": code
    }

@app.post("/api/v1/auth/confirm-phone")
def confirm_phone(data: PhoneConfirm):
    pending = pending_confirmations_db.get(data.phone)
    if not pending or pending["code"] != data.confirmation_code:
        raise HTTPException(status_code=400, detail="Code de confirmation incorrect.")
    
    new_user = {
        "id": len(fake_users_db) + 1,
        "name": pending["name"],
        "phone": pending["phone"],
        "token": f"token-sahel-phone-{len(fake_users_db) + 1}"
    }
    fake_users_db.append(new_user)
    del pending_confirmations_db[data.phone]
    return {"message": "Compte confirmé avec succès !", "user": new_user}

@app.post("/api/v1/auth/login-phone")
def login_phone(user: PhoneLogin):
    for u in fake_users_db:
        if u.get("phone") == user.phone:
            return {"message": "Connexion réussie", "token": u["token"], "name": u["name"]}
    return {"message": "Connexion réussie (Mode Démo)", "token": "token-demo-phone", "name": "Agriculteur Tchad"}

# --- ROUTES PARCELLES & DIAGNOSTICS IA ---

@app.get("/api/v1/parcels")
def get_parcels():
    return fake_parcels_db

@app.post("/api/v1/parcels")
def create_parcel(parcel: ParcelCreate):
    new_id = len(fake_parcels_db) + 1
    # Détection automatique de la zone géographique
    zone = "Sud-Ouest" if parcel.latitude < 10.5 else "Sahel"
    new_parcel = {
        "id": new_id,
        "name": parcel.name,
        "latitude": parcel.latitude,
        "longitude": parcel.longitude,
        "crop_type": parcel.crop_type,
        "area_ha": parcel.area_ha,
        "zone": zone
    }
    fake_parcels_db.append(new_parcel)
    return new_parcel

@app.get("/api/v1/parcels/{parcel_id}/water-balance")
def get_water_balance(parcel_id: int):
    return {
        "etc_mm": 4.8,
        "precipitation_mm": 12.0,
        "deficit_mm": 1.2,
        "recommended_irrigation_m3": 45.0,
        "status": "MODERATE_WATER_NEED"
    }

@app.get("/api/v1/parcels/{parcel_id}/ai-advice")
def get_ai_agronomic_advice(parcel_id: int):
    parcel = next((p for p in fake_parcels_db if p["id"] == parcel_id), None)
    crop = parcel["crop_type"] if parcel else "Culture"
    
    if crop in ["Coton", "Manioc", "Arachide", "Sésame", "Anacarde"]:
        return {
            "threats": f"Risque de chenilles de la capsule sur {crop} et érosion des sols lourds.",
            "preventive_action": "Application de biopesticides locaux et réalisation de bandes enherbées antierosion.",
            "crop_recommendation": f"Rotation conseillée : {crop} suivi de Légumineuses (Arachide/Niébé) pour enrichir le sol en azote.",
            "soil_water_tip": "Paillage végétal dense pour conserver l'humidité et protéger contre le ruissellement."
        }
    else:
        return {
            "threats": "Risque élevé de chenilles légionnaires et stress hydrique thermique.",
            "preventive_action": "Traitement préventif à l'extrait de graines de Neem.",
            "crop_recommendation": "Cultures associées en Push-Pull (Céréales + Légumineuses).",
            "soil_water_tip": "Irrigation goutte-à-goutte ou aux heures fraîches de la matinée."
        }

@app.get("/api/v1/parcels/{parcel_id}/reforestation-ai")
def get_reforestation_advice(parcel_id: int):
    parcel = next((p for p in fake_parcels_db if p["id"] == parcel_id), None)
    is_south = parcel and parcel.get("latitude", 12.0) < 10.5
    
    if is_south:
        # Espèces adaptées à la zone Soudanienne / Sud-Ouest
        reforestation_recommendations = [
            {
                "species_local": "Vitellaria paradoxa (Arbre à Karité)",
                "benefits": "Production de beurre de karité à haute valeur économique, amélioration du microclimat et préservation de la biodiversité.",
                "planting_method": "Protection des jeunes pousses naturelles (RNA) et intégration dans les parcs agroforestiers.",
                "drought_resistance": "Élevée (arbre rustique des savanes soudaniennes)."
            },
            {
                "species_local": "Parkia biglobosa (Néré)",
                "benefits": "Production de graines riches en protéines (Soumbala/Moutarde locale), enrichissement des sols en azote.",
                "planting_method": "Plantation en bordure des champs et espaces communautaires.",
                "drought_resistance": "Excellente adaptation au climat soudano-sahélien."
            },
            {
                "species_local": "Khaya senegalensis (Caïlcedrat / Acajou du Sénégal)",
                "benefits": "Arbre d'ombrage majeur, bois d'œuvre précieux, régulation thermique et lutte contre l'érosion hydrique.",
                "planting_method": "Alignement le long des voies d'accès et limites de parcelles.",
                "drought_resistance": "Forte tolérance aux saisons sèches prolongées."
            }
        ]
        analysis = "Zone Soudanienne / Sud-Ouest : Haut potentiel d'agroforesterie durable et de parcs boisés économiques."
    else:
        # Espèces adaptées au Sahel (Nord / Centre)
        reforestation_recommendations = [
            {
                "species_local": "Acacia senegal (Gommier blanc / Verek)",
                "benefits": "Fixation de l'azote, production de gomme arabique, fixation des dunes et freinement du désert.",
                "planting_method": "Semis en cuvettes Zaï ou demi-lunes pour stocker les eaux de pluie.",
                "drought_resistance": "Extrême (résiste à moins de 300mm de pluie/an)."
            },
            {
                "species_local": "Balanites aegyptiaca (Dattier du désert)",
                "benefits": "Fourrage de saison sèche, fruits et huiles comestibles, barrière anti-vent efficace.",
                "planting_method": "Haies vives protectrices autour des parcelles maraîchères.",
                "drought_resistance": "Maximale grâce à son ancrage racinaire profond."
            }
        ]
        analysis = "Zone Sahélienne : Priorité à la fixation des sols, aux haies brise-vent et au reverdissement anti-sécheresse."
        
    return {
        "zone_analysis": analysis,
        "recommended_trees": reforestation_recommendations,
        "global_strategy": "Déploiement de la Régénération Naturelle Assistée (RNA) et des cuvettes d'infiltration."
    }

@app.get("/api/v1/trainings")
def get_trainings():
    return fake_trainings_db

@app.get("/api/v1/community")
def get_community_posts():
    return fake_community_posts

@app.post("/api/v1/community")
def create_community_post(post: PostCreate):
    new_post = {
        "id": len(fake_community_posts) + 1,
        "author": post.author,
        "message": post.message,
        "date": "À l'instant"
    }
    fake_community_posts.insert(0, new_post)
    return new_post

@app.get("/api/v1/parcels/{parcel_id}/export/{file_format}")
def export_report(parcel_id: int, file_format: str):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Parcelle ID", "Diagnostic", "Statut"])
    writer.writerow([parcel_id, "Conforme", "OK"])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=rapport_parcelle_{parcel_id}.csv"}
    )

# --- ASSISTANT CHATBOT AGRONOMIQUE INTELLIGENT ---

class ChatQuery(BaseModel):
    message: str
    zone: Optional[str] = "Sahel"

@app.post("/api/v1/chat")
def chatbot_assistant(query: ChatQuery):
    msg = query.message.lower()
    zone = query.zone
    
    # Moteur de règles expert pour le contexte sahélien et soudanien
    if "chenille" in msg or "ravageur" in msg or "parasite" in msg or "insecte" in msg:
        response = "🐛 **Conseil anti-ravageurs :** Pour lutter contre les chenilles (légionnaires ou foreurs), utilisez un extrait de décoction de feuilles/graines de Neem. Évitez l'usage excessif de produits chimiques pour protéger la microfaune du sol."
    elif "eau" in msg or "irrigation" in msg | "sécheresse" in msg or "pluie" in msg or "Arrosage" in msg:
        response = "💧 **Gestion de l'eau :** Arrosez de préférence tôt le matin ou tard le soir pour minimiser l'évaporation. En zone aride, privilégiez les techniques de cuvettes (Zaï ou demi-lunes) pour concentrer l'eau de pluie aux pieds des cultures."
    elif "arbre" in msg or "reboisement" in msg or "planter" in msg or "gomme" in msg:
        if zone == "Sud-Ouest":
            response = "🌳 **Reboisement (Sud-Ouest) :** Dans la zone soudanienne, plantez en priorité du Karité (Vitellaria paradoxa), du Néré (Parkia biglobosa) et du Caïlcedrat pour renforcer l'agroforesterie."
        else:
            response = "🌳 **Reboisement (Sahel) :** Dans la zone sahélienne, privilégiez l'Acacia senegal (pour la gomme et la fixation des sols) et le Balanites aegyptiaca (dattier du désert) très résistant à la sécheresse."
    elif "coton" in msg or "manioc" in msg or "arachide" in msg or "sorgho" in msg or "maïs" in msg:
        response = f"🌱 **Culture ({msg}) :** Pratiquez une rotation des cultures (alterner céréales et légumineuses comme l'arachide ou le niébé) et maintenez un paillage organique pour protéger le sol du rayonnement solaire."
    else:
        response = f"👋 Bonjour ! En tant qu'expert agronomique de Tumaï Green Sahel pour la zone **{zone}**, je suis là pour vous conseiller. Posez-moi vos questions sur l'irrigation, la protection contre les ravageurs, ou le choix des arbres de la Grande Muraille Verte !"
        
    return {"response": response}

# --- MODULE MÉTÉO & ALERTES CLIMATIQUES ---

@app.get("/api/v1/parcels/{parcel_id}/weather")
def get_parcel_weather(parcel_id: int):
    parcel = next((p for p in fake_parcels_db if p["id"] == parcel_id), None)
    is_south = parcel and parcel.get("latitude", 12.0) < 10.5
    
    if is_south:
        return {
            "temperature_c": 31.5,
            "humidity_percent": 68,
            "precipitation_mm": 15.2,
            "condition": "Orages isolés & Pluies modérées",
            "alert": "⚠️ Risque de ruissellement fort : vérifiez les bandes d'arrêt et drainage de la parcelle."
        }
    else:
        return {
            "temperature_c": 39.8,
            "humidity_percent": 22,
            "precipitation_mm": 0.0,
            "condition": "Très chaud & Vent sec",
            "alert": "⚠️ Alerte Canicule & Vent de Sable : renforcez le paillage aux pieds des cultures et protégez les jeunes plants."
        }

@app.get("/")
def read_root():
    return {"status": "ok", "message": "API SahelClimate-AI est en ligne"}
