# WhatsApp Chatbot

Este proyecto implementa un asistente conversacional de IA para WhatsApp, diseñado para actuar como el recepcionista virtual de una cafetería ficticia llamada "La Semilla Café". Construido sobre una **arquitectura de agentes con LangGraph**, el bot puede responder preguntas sobre el menú, tomar pedidos, gestionar un carrito de compras y guiar al usuario hasta la finalización del pago de forma robusta y conversacional.

## Características Principales

- **Agente con LangGraph:** Orquestación de herramientas (RAG, carrito, checkout, hablar con humano) guiada por el LLM para decisiones dinámicas durante la conversación.
- **RAG Persistente con ChromaDB:** Indexa `data/knowledge_base/knowledge_base.txt` y responde con información verificada del negocio.
- **Memoria Conversacional + Carritos en Redis:** Persistencia por usuario para continuidad entre reinicios y soporte de escalado horizontal.
- **Carrito y Checkout:** Agregar/ver productos y generar enlace de pago con MercadoPago.
- **Docker Compose listo para desarrollo:** Levanta API, Redis y ngrok en un solo comando.
- **Herramientas modulares (@tool):** Facilitan la extensión de capacidades sin tocar la lógica central.

## Arquitectura y Tecnologías

- **API:** FastAPI + Uvicorn
- **Agentes:** LangGraph (LangChain) + OpenAI
- **Vector DB:** ChromaDB (persistente en `data/chroma_db/`)
- **Estado:** Redis (memoria conversacional y carritos)
- **Mensajería:** Twilio WhatsApp
- **Pagos:** MercadoPago SDK/API
- **Orquestación:** Docker Compose (servicios: app, redis, ngrok)

## Configuración del Entorno

Sigue estos pasos para configurar y ejecutar el proyecto en tu entorno local.

### 1. Prerrequisitos

- Python 3.10+
- Docker y Docker Compose
- Una cuenta de Twilio con un número de WhatsApp activado.
- Una cuenta de MercadoPago para obtener credenciales de API.

### 2. Clonar el Repositorio

```bash
git clone https://github.com/adriancolunga/ecommerce-chatbot.git
cd ecommerce-chatbot
```

### 3. Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto, basándote en `.env.example`:

```ini
# OpenAI
OPENAI_API_KEY="tu_api_key_de_openai"

# Twilio WhatsApp
TWILIO_ACCOUNT_SID="tu_account_sid_de_twilio"
TWILIO_AUTH_TOKEN="tu_auth_token_de_twilio"
TWILIO_WHATSAPP_NUMBER="whatsapp:+NNNN"

# MercadoPago
MERCADOPAGO_ACCESS_TOKEN="tu_access_token_de_mercadopago"

# Notificaciones a humano
HUMAN_CONTACT_NUMBER="whatsapp:+NNNN"

# Ngrok
NGROK_AUTHTOKEN="tu_authtoken_de_ngrok"

# Redis
REDIS_URL="redis://redis:6379"  # usar este valor si levantas con docker-compose
```

## Cómo Ejecutar el Proyecto

### Opción A: Usando Docker (Recomendado)

Levanta toda la stack (API + Redis + ngrok):

```bash
docker-compose up --build
```

- API: `http://localhost:8000` (health-check en `/` y docs en `/docs`).
- ngrok expondrá el puerto 8000 (requiere `NGROK_AUTHTOKEN` en `.env`).

### Opción B: Ejecución Local (para Desarrollo)

1.  **Crear un entorno virtual e instalar dependencias:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

2.  **Iniciar la aplicación:**

    ```bash
    uvicorn main:app
    ```

    La API estará disponible en `http://localhost:8000`.

## Configuración del Webhook de Twilio

- Si usas `docker-compose`, ya corre un contenedor de ngrok que tuneliza `whatsapp-assistant:8000`.
- Obtén la URL pública desde la UI de ngrok en `http://localhost:4040`.
- Configura en Twilio (Messaging → A message comes in): `https://<NGROK_URL>/api/v1/webhook` (método POST).