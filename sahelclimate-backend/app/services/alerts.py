import re
from typing import Dict, Any, Optional

class AlertDispatcher:
    """
    Gestionnaire d'envoi d'alertes via SMS (Gateway local Quectel / AT Commands) ou WhatsApp.
    """

    @staticmethod
    def validate_phone(phone_number: Optional[str]) -> str:
        """Nettoie et formate le numéro au format E.164 ou standard local."""
        if not phone_number:
            return "+23560000000"  # Numéro fallback pour démo/test
        clean = re.sub(r"[^\d+]", "", phone_number)
        return clean

    @classmethod
    def dispatch_sms(cls, phone_number: str, message: str) -> Dict[str, Any]:
        """
        Simule ou exécute l'envoi via passerelle GSM / Modem LTE (ex: Quectel EC25).
        """
        formatted_phone = cls.validate_phone(phone_number)
        # Logique de commande AT / Gateway HTTP
        return {
            "channel": "SMS",
            "provider": "GSM_Gateway_Quectel_EC25",
            "recipient": formatted_phone,
            "message_length": len(message),
            "status": "DELIVERED",
            "gateway_response": f"AT+CMGS OK - Message sent to {formatted_phone}"
        }

    @classmethod
    def dispatch_whatsapp(cls, phone_number: str, message: str) -> Dict[str, Any]:
        """
        Simule l'envoi via l'API WhatsApp Business.
        """
        formatted_phone = cls.validate_phone(phone_number)
        return {
            "channel": "WhatsApp",
            "provider": "WhatsApp_Business_API",
            "recipient": formatted_phone,
            "message_length": len(message),
            "status": "DELIVERED",
            "wa_message_id": f"WAMID.{formatted_phone[-8:]}.sahel"
        }

    @classmethod
    def send(cls, channel: str, phone_number: Optional[str], parcel_id: int, custom_msg: Optional[str] = None) -> Dict[str, Any]:
        channel_upper = channel.upper()
        
        # Message automatique basé sur le diagnostic si aucun message custom n'est fourni
        text = custom_msg or f"[SahelClimate] Alerte d'irrigation pour la parcelle #{parcel_id}. Révision du bilan hydrique requise."

        if "WHATSAPP" in channel_upper:
            dispatch_res = cls.dispatch_whatsapp(phone_number, text)
        else:
            dispatch_res = cls.dispatch_sms(phone_number, text)

        return {
            "status": "DISPATCHED",
            "message": f"Alerte envoyée via {channel_upper} pour la parcelle {parcel_id}",
            "dispatch_details": dispatch_res
        }
