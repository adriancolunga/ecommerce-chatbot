import logging
import os
import json
import redis
from langchain_core.tools import tool
from core.rag_manager import RAGManager
from services.payment_manager import create_payment_link
from services.whatsapp_client import send_message

redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://redis:6379"))

def _get_cart(user_id: str) -> list:
    """Recupera el carrito de un usuario desde Redis."""
    cart_json = redis_client.get(f"cart:{user_id}")
    return json.loads(cart_json) if cart_json else []

def _save_cart(user_id: str, cart: list):
    """Guarda el carrito de un usuario en Redis."""
    redis_client.set(f"cart:{user_id}", json.dumps(cart))

def _delete_cart(user_id: str):
    """Elimina el carrito de un usuario de Redis."""
    redis_client.delete(f"cart:{user_id}")

# --- RAG Manager --- 
rag_manager = RAGManager()
rag_manager.load_vector_store()

def _get_product_price(item_name: str) -> int:
    """Busca el precio de un producto en products.json por su nombre o alias."""
    try:
        with open('data/products.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        normalized_item_name = item_name.lower().strip()
        
        for product in data['productos']:
            if normalized_item_name == product['nombre_oficial'].lower():
                return product['precio']
            for alias in product.get('alias', []):
                if normalized_item_name == alias.lower():
                    return product['precio']
        
        logging.warning(f"Producto '{item_name}' no encontrado en products.json")
        return 0
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Error al leer o procesar products.json: {e}")
        return 0

@tool
def get_knowledge_base_response(user_query: str) -> str:
    """Consulta la base de conocimientos para obtener contexto y responder preguntas del usuario.
    Úsala para obtener información sobre el menú, horarios, o cualquier dato sobre La Semilla Café.
    Devuelve el texto relevante encontrado, que el agente usará para construir la respuesta final.
    """
    logging.info(f"Ejecutando get_knowledge_base_response con la consulta: {user_query}")
    try:
        retriever = rag_manager.get_retriever()
        relevant_docs = retriever.invoke(user_query)
        context = "\n\n---\n\n".join([doc.page_content for doc in relevant_docs])
        
        if not context:
            return "No encontré información relevante sobre eso en mi base de conocimientos."
        
        return f"Contexto encontrado para la pregunta '{user_query}':\n{context}"
    except Exception as e:
        logging.error(f"Error en get_knowledge_base_response: {e}")
        return "Ocurrió un error al consultar la base de conocimientos."

@tool
def add_item_to_cart(user_id: str, item_name: str, quantity: int) -> str:
    """Añade un producto con su cantidad al carrito de compras del usuario.
    Usa esta herramienta cuando el usuario pida explícitamente agregar algo a su pedido.
    """
    logging.info(f"Añadiendo {quantity} de '{item_name}' al carrito de {user_id}")

    price = _get_product_price(item_name)
    if price == 0:
        return f"Lo siento, no encontré el producto '{item_name}'. ¿Podrías verificar el nombre e intentarlo de nuevo?"

    cart = _get_cart(user_id)

    for item in cart:
        if item['item_name'].lower() == item_name.lower().strip():
            item['quantity'] += quantity
            _save_cart(user_id, cart)
            return f"{quantity} x {item_name} más añadido(s). Ahora tienes {item['quantity']} en total."

    cart.append({"item_name": item_name, "quantity": quantity, "price": price})
    _save_cart(user_id, cart)
    return f"{quantity} x {item_name} ha(n) sido añadido(s) a tu carrito."

@tool
def view_cart(user_id: str) -> str:
    """Muestra el contenido actual del carrito de compras del usuario, incluyendo productos, cantidades y subtotal.
    Usa esta herramienta si el usuario pregunta qué hay en su carrito o cuál es el total hasta ahora.
    """
    logging.info(f"Mostrando carrito para {user_id}")
    cart_items = _get_cart(user_id)
    if not cart_items:
        return "Tu carrito está vacío."

    response_lines = ["Este es tu carrito:"]
    total = 0
    for item in cart_items:
        price = item.get('price', 0)
        subtotal = item['quantity'] * price
        response_lines.append(f"- {item['quantity']} x {item['item_name']}: ${subtotal}")
        total += subtotal
    
    response_lines.append(f"\nTotal: ${total}")
    return "\n".join(response_lines)

@tool
def checkout(user_id: str) -> str:
    """Finaliza el pedido del usuario, genera un enlace de pago y vacía el carrito.
    Usa esta herramienta SOLO cuando el usuario confirme explícitamente que quiere pagar o finalizar su pedido.
    """
    logging.info(f"Iniciando checkout para {user_id}")
    cart_items = _get_cart(user_id)
    if not cart_items:
        return "Tu carrito está vacío. No puedes finalizar un pedido sin productos."

    cart_items_for_payment = []
    for item in cart_items:
        cart_items_for_payment.append({
            "title": item['item_name'],
            "quantity": item['quantity'],
            "unit_price": item.get('price', 0)
        })

    payment_link = create_payment_link(cart_items_for_payment, user_id)
    
    if payment_link:
        _delete_cart(user_id)
        return f"Tu pedido está listo. Aquí tienes tu enlace de pago: {payment_link}"
    else:
        return "Tuvimos un problema al generar tu enlace de pago. Por favor, intenta de nuevo."

@tool
def talk_to_human(user_id: str, reason: str) -> str:
    """Transfiere la conversación a un agente humano cuando el usuario lo solicita o tiene un problema complejo.
    Usa esta herramienta si el usuario pide hablar con una persona o si sus preguntas están fuera de tu alcance.
    """
    logging.info(f"Usuario {user_id} solicita hablar con un humano. Motivo: {reason}")
    human_contact = os.getenv("HUMAN_CONTACT_NUMBER")
    if human_contact:
        notification_message = f"Atención: Cliente {user_id} necesita ayuda. Motivo: '{reason}'"
        send_message(to=human_contact, body=notification_message)
        return "He notificado a uno de nuestros agentes para que se ponga en contacto contigo. Te atenderán pronto."
    else:
        logging.warning("HUMAN_CONTACT_NUMBER no está configurado.")
        return "Me gustaría pasarte con un humano, pero no tengo a quién contactar. Disculpa las molestias."
