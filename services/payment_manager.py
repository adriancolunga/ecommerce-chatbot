import os
import logging
import mercadopago

MERCADOPAGO_ACCESS_TOKEN = os.getenv("MERCADOPAGO_ACCESS_TOKEN")

sdk = None
if MERCADOPAGO_ACCESS_TOKEN:
    try:
        sdk = mercadopago.SDK(MERCADOPAGO_ACCESS_TOKEN)
        logging.info("SDK de MercadoPago inicializado correctamente.")
    except Exception as e:
        logging.error(f"Error al inicializar el SDK de MercadoPago: {e}")
else:
    logging.warning("La credencial MERCADOPAGO_ACCESS_TOKEN no está configurada. La creación de pagos está deshabilitada.")

def create_payment_link(cart_items: list, user_id: str) -> str | None:
    """
    Crea una preferencia de pago en MercadoPago y devuelve el link de pago.

    Args:
        cart_items (list): Una lista de diccionarios, donde cada diccionario representa un item.
                           Ej: [{'title': 'Brownie', 'quantity': 2, 'unit_price': 50}]
        user_id (str): El identificador del usuario para asociarlo al pago.

    Returns:
        str | None: La URL de pago (init_point) si es exitoso, o None si falla.
    """
    if not sdk:
        logging.error("Intento de crear un pago fallido: el SDK de MercadoPago no está inicializado.")
        return None

    try:
        preference_data = {
            "items": cart_items,
            "payer": {
                "name": user_id
            },
            "auto_return": "approved", # Redirige automáticamente al cliente tras el pago
            "external_reference": f"pedido_{user_id}_{os.urandom(4).hex()}" # Referencia única para nuestro sistema
        }

        logging.info(f"Creando preferencia de pago para {user_id} con items: {cart_items}")
        preference_response = sdk.preference().create(preference_data)
        preference = preference_response["response"]

        payment_link = preference["init_point"]
        logging.info(f"Link de pago generado para {user_id}: {payment_link}")
        
        return payment_link

    except Exception as e:
        logging.error(f"Error al crear la preferencia de pago en MercadoPago para {user_id}: {e}", exc_info=True)
        return None
