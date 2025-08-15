# WhatsApp AI Assistant para "La Semilla Café"

Este proyecto implementa un asistente conversacional de IA para WhatsApp, diseñado para actuar como el recepcionista virtual de una cafetería ficticia llamada "La Semilla Café". Construido sobre una **arquitectura de agentes con LangGraph**, el bot puede responder preguntas sobre el menú, tomar pedidos, gestionar un carrito de compras y guiar al usuario hasta la finalización del pago de forma robusta y conversacional.

## Características Principales

- **Arquitectura de Agentes con LangGraph:** En lugar de depender de reglas fijas o regex, el sistema utiliza un agente inteligente orquestado por LangGraph. El agente decide qué herramienta usar (consultar la base de conocimientos, añadir al carrito, pagar) basándose en el flujo de la conversación, lo que lo hace más flexible y robusto.
- **Base de Conocimientos Persistente (RAG):** Se basa en un sistema de `Retrieval-Augmented Generation` con **ChromaDB** para responder únicamente con información verificada de un documento de texto. La base de datos vectorial es persistente, eliminando la necesidad de recrearla en cada reinicio.
- **Memoria Conversacional por Usuario:** Recuerda el historial de la conversación con cada cliente, permitiendo un diálogo fluido y preguntas de seguimiento.
- **Lógica de Carrito de Compras:** Permite a los usuarios añadir múltiples productos, ver su pedido y recibir el total calculado.
- **Integración de Pagos:** Se conecta con la API de MercadoPago para generar un enlace de pago único y dinámico por el total del pedido.
- **Despliegue Sencillo con Docker y Ngrok:** Totalmente containerizado. Incluye un servicio de **ngrok** en `docker-compose.yml` que expone automáticamente el webhook local, simplificando drásticamente el entorno de desarrollo.
- **Herramientas Modulares:** Cada capacidad del bot (consultar el menú, ver el carrito, hablar con un humano) está encapsulada en una "herramienta" discreta, facilitando la adición de nuevas funcionalidades sin alterar la lógica principal.

## Arquitectura y Tecnologías

- **Framework de API:** FastAPI
- **Servidor ASGI:** Uvicorn
- **Orquestación de Contenedores:** Docker & Docker Compose
- **Core de IA y Agentes:** LangChain & LangGraph
- **Modelos de Lenguaje y Embeddings:** OpenAI
- **Base de Datos Vectorial:** ChromaDB
- **Integración de Pagos:** MercadoPago API
- **Túnel de Desarrollo:** Ngrok
- **Integración con WhatsApp:** Twilio API for WhatsApp
- **Pasarela de Pagos:** MercadoPago SDK

## Configuración del Entorno

Sigue estos pasos para configurar y ejecutar el proyecto en tu entorno local.

### 1. Prerrequisitos

- Python 3.10+
- Docker y Docker Compose
- Una cuenta de Twilio con un número de WhatsApp activado.
- Una cuenta de MercadoPago para obtener credenciales de API.

### 2. Clonar el Repositorio

```bash
git clone https://github.com/adriancolunga/whatsapp-ai-recepcionist.git
cd whatsapp-ai-recepcionist
```

### 3. Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto, basándote en el archivo `.env.example`. Completa los valores requeridos:

```ini
# Credenciales de OpenAI
OPENAI_API_KEY="tu_api_key_de_openai"

# Credenciales de Twilio
TWILIO_ACCOUNT_SID="tu_account_sid_de_twilio"
TWILIO_AUTH_TOKEN="tu_auth_token_de_twilio"
TWILIO_WHATSAPP_NUMBER="whatsapp:el_numero_de_twilio"

# Credenciales de MercadoPago
MERCADOPAGO_ACCESS_TOKEN="tu_access_token_de_mercadopago"
```

### 4. Construir la Base de Conocimientos

El asistente basa sus respuestas en el archivo `data/knowledge_base/knowledge_base.txt`. Si modificas este archivo, necesitas reconstruir el índice vectorial. El sistema lo hace automáticamente al iniciar, pero también puedes forzarlo manualmente.

## Cómo Ejecutar el Proyecto

### Opción A: Usando Docker (Recomendado)

Con Docker, puedes levantar todo el servicio con un solo comando:

```bash
docker-compose up --build
```

La API estará disponible en `http://localhost:8000`.

### Opción B: Ejecución Local (para Desarrollo)

1.  **Crear un entorno virtual e instalar dependencias:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

2.  **Iniciar la aplicación:**

    ```bash
    uvicorn main:app --reload
    ```

    La API estará disponible en `http://localhost:8000`.

## Configuración del Webhook de Twilio

Para que Twilio pueda comunicarse con tu aplicación, necesitas exponer tu `localhost` a internet. Puedes usar una herramienta como `ngrok`.

1.  **Ejecuta ngrok:**

    ```bash
    ngrok http 8000
    ```

2.  **Copia la URL `https`** que te proporciona ngrok (ej: `https://xxxx-xxxx.ngrok.io`).

3.  **Configura el webhook en Twilio:**
    -   Ve a la configuración de tu número de WhatsApp en la consola de Twilio.
    -   En la sección "Messaging", busca "A message comes in".
    -   Pega la URL de ngrok y añade la ruta `/api/v1/webhook`. Ejemplo: `https://xxxx-xxxx.ngrok.io/api/v1/webhook`.
    -   Asegúrate de que el método sea `HTTP POST`.
    -   Guarda los cambios.

¡Y listo! Ahora puedes enviar un mensaje a tu número de WhatsApp de Twilio y conversar con tu asistente de IA.
