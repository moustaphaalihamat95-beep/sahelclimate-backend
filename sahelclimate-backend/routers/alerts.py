from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from services.notification import send_irrigation_alert_sms, send_irrigation_alert_whatsapp

router = APIRouter(prefix="/api/v1/alerts", tags=["Alerts"])

class AlertRequest(BaseModel):
    parcel_id: int
    parcel_name: str
    phone_number: str
    water_deficit_mm: float
    total_volume_m3: float
    channel: str = "sms"

@router.post("/dispatch-irrigation")
def dispatch_alert(payload: AlertRequest, background_tasks: BackgroundTasks):
    if payload.channel == "whatsapp":
        background_tasks.add_task(
            send_irrigation_alert_whatsapp,
            payload.phone_number,
            payload.parcel_name,
            payload.total_volume_m3
        )
    else:
        background_tasks.add_task(
            send_irrigation_alert_sms,
            payload.phone_number,
            payload.parcel_name,
            payload.total_volume_m3
        )
    
    return {
        "status": "success",
        "message": f"Alerte {payload.channel.upper()} programmée pour {payload.phone_number}"
    }
