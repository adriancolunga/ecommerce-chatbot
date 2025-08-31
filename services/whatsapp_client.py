import os
import logging
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

try:
    if ACCOUNT_SID and AUTH_TOKEN:
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
    else:
        client = None
        logging.warning("Las credenciales de Twilio (ACCOUNT_SID, AUTH_TOKEN) no están configuradas. El envío de mensajes está deshabilitado.")
except Exception as e:
    client = None
    logging.error(f"Error al inicializar el cliente de Twilio: {e}")

def send_message(to: str, body: str):
    """
    Envía un mensaje de WhatsApp utilizando la API de Twilio.
    """
    if not client or not TWILIO_NUMBER:
        logging.error(f"Intento de envío a {to} fallido: El cliente de Twilio o el número de origen no están configurados.")
        return

    try:
        logging.info(f"Enviando mensaje a {to}...")
        message = client.messages.create(
            from_=TWILIO_NUMBER,
            body=body,
            to=to
        )
        logging.info(f"Mensaje enviado a {to} con SID: {message.sid}")
    except TwilioRestException as e:
        if e.code == 63038:
            logging.error(
                "Error de Twilio: Límite de mensajes de la cuenta de prueba superado. "
                "Para seguir enviando mensajes, actualiza tu cuenta de Twilio a una versión de pago."
            )
        else:
            logging.error(f"Error de la API de Twilio al enviar a {to}: {e}", exc_info=True)
    except Exception as e:
        logging.error(f"Error inesperado al enviar el mensaje a {to}: {e}", exc_info=True)