import logging
from langchain_core.messages import HumanMessage
from core.graph import app, system_message

class WhatsappAssistant:
    """
    Gestiona el estado de las conversaciones y sirve como punto de entrada al grafo de LangGraph.
    """
    def __init__(self):
        """Inicializa el asistente, manteniendo un registro de los hilos de conversación."""
        self.conversation_threads = {}
        logging.info("WhatsappAssistant (LangGraph version) inicializado.")

    def get_response(self, user_id: str, user_query: str) -> str:
        """Obtiene una respuesta del agente de LangGraph para un usuario y una consulta dados."""
        logging.info(f"Procesando mensaje de {user_id} con LangGraph.")

        if user_id not in self.conversation_threads:
            self.conversation_threads[user_id] = [system_message]
            logging.info(f"Nuevo hilo de conversación creado para {user_id}.")
        self.conversation_threads[user_id].append(HumanMessage(content=user_query))

        graph_input = {"messages": self.conversation_threads[user_id]}
        final_response = None
        for event in app.stream(graph_input):
            if "agent" in event:
                final_response = event["agent"]["messages"][-1]
            elif "__end__" in event:
                final_response = event["__end__"]["messages"][-1]

        if not final_response:
            logging.error("El grafo de LangGraph no produjo una respuesta final.")
            return "Lo siento, tuve un problema para procesar tu mensaje."

        self.conversation_threads[user_id].append(final_response)
        return final_response.content

    def clear_memory(self, user_id: str):
        """Borra el historial de conversación para un usuario específico."""
        if user_id in self.conversation_threads:
            self.conversation_threads.pop(user_id)
            logging.info(f"Historial de conversación para {user_id} borrado.")
