from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from services.report import generate_water_balance_excel, generate_water_balance_pdf

router = APIRouter(prefix="/api/v1/parcels", tags=["Reports"])

# Données factices pour la démonstration
DUMMY_RECORDS = [
    {"date": "2026-10-07", "et0": 5.40, "etc": 3.78, "rain": 0.0, "deficit": 3.78, "volume_m3": 94.5, "status": "Irrigation requise"},
    {"date": "2026-10-08", "et0": 5.52, "etc": 3.86, "rain": 0.0, "deficit": 3.86, "volume_m3": 96.5, "status": "Irrigation requise"},
    {"date": "2026-10-09", "et0": 5.49, "etc": 3.84, "rain": 0.0, "deficit": 3.84, "volume_m3": 96.0, "status": "Irrigation requise"}
]

@router.get("/{parcel_id}/export/excel")
def export_excel(parcel_id: int):
    excel_stream = generate_water_balance_excel(f"Parcelle #{parcel_id}", "Sésame", DUMMY_RECORDS)
    headers = {'Content-Disposition': f'attachment; filename="bilan_hydrique_parcelle_{parcel_id}.xlsx"'}
    return StreamingResponse(
        excel_stream,
        headers=headers,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@router.get("/{parcel_id}/export/pdf")
def export_pdf(parcel_id: int):
    pdf_stream = generate_water_balance_pdf(f"Parcelle #{parcel_id}", "Sésame", DUMMY_RECORDS)
    headers = {'Content-Disposition': f'attachment; filename="bilan_hydrique_parcelle_{parcel_id}.pdf"'}
    return StreamingResponse(
        pdf_stream,
        headers=headers,
        media_type="application/pdf"
    )
