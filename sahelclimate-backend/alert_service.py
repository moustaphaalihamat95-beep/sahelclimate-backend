import logging
import os
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AlertService")

class NotificationGateway:
    """
    Gestionnaire d'envoi d'alertes météo-agronomiques par SMS et WhatsApp.
    """

    @staticmethod
    def format_irrigation_sms(
        farmer_name: str,
        parcel_name: str,
        crop_type: str,
        water_volume_m3: float,
        recommendation: str
    ) -> str:
        """
        Formate un message SMS court et optimisé pour le réseau cellulaire sahélien.
        """
        return (
            f"SahelClimate-AI Alerte\n"
            f"Agriculteur: {farmer_name}\n"
            f"Parcelle: {parcel_name} ({crop_type})\n"
            f"Besoin d'eau cette semaine: {water_volume_m3} m3\n"
            f"Consigne: {recommendation}"
        )

    @classmethod
    async def send_sms_alert(cls, phone_number: str, message: str) -> Dict[str, Any]:
        """
        Simule ou déclenche l'envoi d'un SMS via passerelle GSM / Twilio.
        """
        # Intégration future avec passerelle local GSM / Twilio
        logger.info(f"[SMS ENVOYÉ] Destinataire: {phone_number} | Contenu: {message}")
        
        return {
            "status": "SUCCESS",
            "channel": "SMS",
            "recipient": phone_number,
            "message_length": len(message)
        }

    @classmethod
    async def send_whatsapp_alert(cls, phone_number: str, message: str) -> Dict[str, Any]:
        """
        Simule ou déclenche l'envoi d'un message WhatsApp Business API.
        """
        logger.info(f"[WHATSAPP ENVOYÉ] Destinataire: {phone_number}")
        
        return {
            "status": "SUCCESS",
            "channel": "WhatsApp",
            "recipient": phone_number
        }
