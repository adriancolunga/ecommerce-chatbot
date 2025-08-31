import redis
import logging
import os
from typing import List
from langchain_core.messages import AnyMessage, messages_from_dict, messages_to_dict

logger = logging.getLogger(__name__)

class ConversationManager:
    """
    Gestiona el historial de conversaciones utilizando Redis para persistencia.
    """
    def __init__(self):
        """Inicializa el cliente de Redis."""
        redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()
            logger.info(f"Conectado exitosamente a Redis en {redis_url}")
        except redis.exceptions.ConnectionError as e:
            logger.error(f"No se pudo conectar a Redis: {e}")
            raise

    def _get_key(self, user_id: str) -> str:
        """Genera la clave de Redis para un ID de usuario dado."""
        return f"conversation:{user_id}"

    def get_history(self, user_id: str) -> List[AnyMessage]:
        """Recupera el historial de conversación para un usuario."""
        key = self._get_key(user_id)
        try:
            serialized_messages = self.redis_client.lrange(key, 0, -1)
            if not serialized_messages:
                return []
            
            import json
            deserialized_messages = [json.loads(m) for m in serialized_messages]
            return messages_from_dict(deserialized_messages)
        except Exception as e:
            logger.error(f"Error al recuperar el historial para {user_id}: {e}")
            return []

    def add_message(self, user_id: str, message: AnyMessage):
        """Añade un mensaje al historial de conversación de un usuario."""
        key = self._get_key(user_id)
        try:
            serialized_message = messages_to_dict([message])
            import json
            self.redis_client.rpush(key, json.dumps(serialized_message[0]))
        except Exception as e:
            logger.error(f"Error al añadir mensaje para {user_id}: {e}")

    def clear_history(self, user_id: str):
        """Borra el historial de conversación para un usuario."""
        key = self._get_key(user_id)
        try:
            self.redis_client.delete(key)
            logger.info(f"Historial de conversación para {user_id} borrado.")
        except Exception as e:
            logger.error(f"Error al borrar el historial para {user_id}: {e}")
