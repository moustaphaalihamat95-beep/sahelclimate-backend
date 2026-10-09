import os
from twilio.rest import Client

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "votre_account_sid")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "votre_auth_token")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "+1234567890")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN) if TWILIO_ACCOUNT_SID.startswith("AC") else None

def send_irrigation_alert_sms(phone_number: str, parcel_name: str, volume_m3: float):
    message_body = (
        f"🌱 SahelClimate Alert\n"
        f"Parcelle: {parcel_name}\n"
        f"Irrigation requise aujourd'hui !\n"
        f"Volume recommandé: {volume_m3:.1f} m³ d'eau."
    )
    if client:
        message = client.messages.create(
            body=message_body,
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        return message.sid
    print(f"\n[SIMULATION SMS -> {phone_number}] :\n{message_body}\n")
    return "simulated_sms_id"

def send_irrigation_alert_whatsapp(phone_number: str, parcel_name: str, volume_m3: float):
    message_body = (
        f"🌾 *SahelClimate-AI Notification*\n\n"
        f"📍 *Parcelle :* {parcel_name}\n"
        f"💧 *Action :* Irrigation recommandée\n"
        f"📊 *Volume d'eau requis :* `{volume_m3:.1f} m³`\n\n"
        f"_Optimisez votre récolte en ajustant l'arrosage dès aujourd'hui._"
    )
    recipient = f"whatsapp:{phone_number}" if not phone_number.startswith("whatsapp:") else phone_number
    if client:
        message = client.messages.create(
            body=message_body,
            from_=TWILIO_WHATSAPP_NUMBER,
            to=recipient
        )
        return message.sid
    print(f"\n[SIMULATION WHATSAPP -> {recipient}] :\n{message_body}\n")
    return "simulated_whatsapp_id"
