from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from app.database import get_db
from app.models import ParcelModel
from app.schemas import AlertInput
from app.services.alerts import AlertDispatcher

router = APIRouter(prefix="/api/v1/parcels", tags=["Alerts"])

class CustomAlertInput(AlertInput):
    custom_message: Optional[str] = None

@router.post("/{parcel_id}/send-alert", summary="Send Alert")
def send_alert(parcel_id: int, alert: CustomAlertInput, db: Session = Depends(get_db)):
    parcel = db.query(ParcelModel).filter(ParcelModel.id == parcel_id).first()
    if not parcel:
        raise HTTPException(status_code=404, detail="Parcelle non trouvée")

    # On utilise le numéro enregistré sur la parcelle s'il existe
    phone = parcel.phone_number or "+23560000000"

    dispatch_result = AlertDispatcher.send(
        channel=alert.channel,
        phone_number=phone,
        parcel_id=parcel_id,
        custom_msg=alert.custom_message
    )

    return dispatch_result
