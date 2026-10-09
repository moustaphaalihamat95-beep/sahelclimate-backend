import io
from fastapi import FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

app = FastAPI(title="SahelClimate-AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Parcel(BaseModel):
    id: Optional[int] = None
    location_name: str
    area_ha: float
    crop_type: Optional[str] = "Maïs"
    ndvi_value: Optional[float] = 0.45

db_parcels = [
    {"id": 1, "location_name": "Parcelle N'Djamena Nord", "area_ha": 15.2, "crop_type": "Maïs", "ndvi_value": 0.52},
    {"id": 2, "location_name": "Zone Bahr El Gazel", "area_ha": 8.7, "crop_type": "Sorgho", "ndvi_value": 0.38},
]

@app.get("/")
def root():
    return {"status": "SahelClimate-AI API opérationnelle"}

@app.get("/sw.js")
def service_worker():
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.get("/api/v1/parcels", response_model=List[Parcel])
def get_parcels():
    return db_parcels

@app.post("/api/v1/parcels", response_model=Parcel)
def create_parcel(parcel: Parcel):
    new_id = len(db_parcels) + 1
    p_dict = parcel.model_dump() if hasattr(parcel, 'model_dump') else parcel.dict()
    p_dict["id"] = new_id
    db_parcels.append(p_dict)
    return p_dict

@app.get("/api/v1/parcels/{parcel_id}/diagnostic")
def get_parcel_diagnostic(parcel_id: int):
    parcel = next((p for p in db_parcels if p["id"] == parcel_id), None)
    if not parcel:
        raise HTTPException(status_code=404, detail="Parcelle introuvable")

    ndvi = parcel.get("ndvi_value", 0.40)
    if ndvi >= 0.50:
        health_status = "Végétation Vigoureuse"
        drought_risk = "Faible"
        irrigation_need = "Maintenir l'arrosage régulier (10-12 mm/semaine)"
        color_code = "green"
    elif 0.35 <= ndvi < 0.50:
        health_status = "Stress Hydrique Modéré"
        drought_risk = "Moyen"
        irrigation_need = "Augmenter la fréquence d'irrigation (18-20 mm/semaine)"
        color_code = "orange"
    else:
        health_status = "Sécheresse / Dégradation Végétale"
        drought_risk = "Élevé"
        irrigation_need = "Irrigation d'urgence requise (25+ mm/semaine)"
        color_code = "red"

    return {
        "parcel_id": parcel["id"],
        "location_name": parcel["location_name"],
        "crop_type": parcel.get("crop_type", "Maïs"),
        "area_ha": parcel["area_ha"],
        "ndvi_value": ndvi,
        "health_status": health_status,
        "drought_risk": drought_risk,
        "color_code": color_code,
        "irrigation_recommendation": irrigation_need,
        "soil_moisture_index": round(ndvi * 0.75, 2),
        "advisory_note": f"Analyse climatique pour {parcel['location_name']}. Recommandations adaptées au climat sahélien."
    }

@app.get("/api/v1/parcels/{parcel_id}/report/pdf")
def generate_pdf_report(parcel_id: int):
    diag = get_parcel_diagnostic(parcel_id)

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)

    # Entête
    p.setFillColor(colors.HexColor("#065F46"))
    p.rect(0, 730, 612, 60, fill=True, stroke=False)

    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 18)
    p.drawString(40, 755, "SahelClimate-AI — Bulletin de Diagnostic Agrométéo")

    # Contenu
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(40, 690, f"Fiche Parcelle #{diag['parcel_id']} : {diag['location_name']}")

    p.setFont("Helvetica", 11)
    p.drawString(40, 660, f"Culture principale : {diag['crop_type']}")
    p.drawString(40, 640, f"Superficie totale : {diag['area_ha']} ha")
    p.drawString(40, 620, f"Indice de Végétation (NDVI) : {diag['ndvi_value']}")

    # Bloc Risque
    p.setFillColor(colors.HexColor("#F3F4F6"))
    p.rect(40, 520, 530, 80, fill=True, stroke=True)

    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(55, 575, f"Niveau de Risque Sécheresse : {diag['drought_risk']}")
    p.setFont("Helvetica", 10)
    p.drawString(55, 555, f"État de santé : {diag['health_status']}")
    p.drawString(55, 535, f"Recommandation : {diag['irrigation_recommendation']}")

    # Note
    p.setFont("Helvetica-Oblique", 9)
    p.drawString(40, 480, f"Note : {diag['advisory_note']}")

    # Pied de page
    p.setFont("Helvetica", 8)
    p.drawString(40, 30, "Généré automatiquement par le système SahelClimate-AI — Données Agrométéo Tchad/Sahel")

    p.showPage()
    p.save()

    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=diagnostic_parcelle_{parcel_id}.pdf"}
    )
