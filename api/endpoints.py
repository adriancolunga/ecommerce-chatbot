import logging
from fastapi import APIRouter, Form, Response
from core.assistant import WhatsappAssistant
from services.whatsapp_client import send_message
from core.tools import rag_manager

router = APIRouter()
assistant = WhatsappAssistant()

@router.post("/webhook")
async def receive_webhook(From: str = Form(...), Body: str = Form(...)):
    """
    Endpoint que recibe los mensajes de Twilio y los procesa con el agente de LangGraph.
    """
    logging.info(f"Mensaje recibido de {From}: '{Body}'")
    user_message = Body.strip().lower()

    try:
        if user_message == 'fin':
            assistant.clear_memory(From)
            send_message(to=From, body="✅ Memoria de conversación borrada. Puedes empezar de cero.")
            return Response(status_code=204)

        if user_message == 'recargar':
            logging.info(f"Peticion de recarga de knowledge base recibida de {From}.")
            # La recarga ahora se hace directamente sobre la instancia del rag_manager
            success = rag_manager.reload_vector_store()
            if success:
                send_message(to=From, body="✅ Base de conocimientos recargada con éxito.")
            else:
                send_message(to=From, body="❌ Error: No se pudo recargar la base de conocimientos.")
            return Response(status_code=204)

        final_response = assistant.get_response(user_id=From, user_query=Body)

        if final_response:
            send_message(to=From, body=final_response)

    except Exception as e:
        logging.error(f"Ocurrió un error al procesar el mensaje de {From}: {e}", exc_info=True)
        error_message = "Lo siento, ocurrió un error inesperado. Por favor, intenta de nuevo más tarde."
        send_message(to=From, body=error_message)

    return Response(status_code=204)