import os
import logging
import requests
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

# Cargar las credenciales desde las variables de entorno
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

# --- Configuración del Proveedor de Mensajería ---
MESSAGING_PROVIDER = os.getenv("MESSAGING_PROVIDER", "twilio").lower()
NODEJS_SERVER_URL = os.getenv("NODEJS_SERVER_URL", "http://localhost:3000")

# Inicializar el cliente de Twilio
# Hacemos esto una vez cuando el módulo se carga para mayor eficiencia.
try:
    if ACCOUNT_SID and AUTH_TOKEN:
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
    else:
        client = None
        logging.warning("Las credenciales de Twilio (ACCOUNT_SID, AUTH_TOKEN) no están configuradas. El envío de mensajes está deshabilitado.")
except Exception as e:
    client = None
    logging.error(f"Error al inicializar el cliente de Twilio: {e}")

def send_message_via_nodejs(to: str, body: str):
    """Envía un mensaje utilizando el servidor puente de Node.js."""
    endpoint = f"{NODEJS_SERVER_URL}/send-message"
    # El número debe estar en formato '54911...' sin el 'whatsapp:+'
    phone_number = to.replace("whatsapp:+", "")
    payload = {"phoneNumber": phone_number, "message": body}
    
    try:
        logging.info(f"Enviando mensaje a {to} vía Node.js: '{body[:50]}...'")
        response = requests.post(endpoint, json=payload, timeout=10)
        response.raise_for_status()
        logging.info(f"Mensaje enviado a {to} vía Node.js con éxito.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error al enviar mensaje a {to} vía Node.js: {e}", exc_info=True)

def send_message_via_twilio(to: str, body: str):
    """
    Envía un mensaje de WhatsApp utilizando la API de Twilio.
    """
    if not client or not TWILIO_NUMBER:
        logging.error(f"Intento de envío a {to} fallido: El cliente de Twilio o el número de origen no están configurados.")
        # En un entorno real, no imprimiríamos el body, pero es útil para depuración.
        logging.debug(f"Mensaje no enviado a {to}: {body}")
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

def send_message(to: str, body: str):
    """
    Envía un mensaje de WhatsApp utilizando el proveedor configurado.

    Args:
        to (str): El número del destinatario en formato 'whatsapp:+54911...'
        body (str): El contenido del mensaje a enviar.
    """
    if MESSAGING_PROVIDER == "nodejs":
        send_message_via_nodejs(to, body)
    elif MESSAGING_PROVIDER == "twilio":
        send_message_via_twilio(to, body)
    else:
        logging.error(f"Proveedor de mensajería no válido: '{MESSAGING_PROVIDER}'. No se envió el mensaje a {to}.")
