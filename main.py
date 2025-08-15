import logging
from fastapi import FastAPI
from api.endpoints import router as api_router
from core.logging_config import configure_logging

configure_logging()

app = FastAPI(
    title="Whatsapp Assistant",
    description="Un chatbot de IA para WhatsApp con base de conocimientos propia.",
    version="0.1.0"
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/", tags=["Health Check"])
def health_check():
    """
    Endpoint de "health check" para verificar que el servidor está funcionando.
    """
    logging.info("Health check endpoint fue invocado.")
    return {"status": "ok", "message": "Whatsapp Assistant is running!"}
