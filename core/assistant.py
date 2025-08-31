import logging
from langchain_core.messages import HumanMessage
from core.graph import app, system_message
from core.memory import ConversationManager

class WhatsappAssistant:
    """
    Gestiona el estado de las conversaciones y sirve como punto de entrada al grafo de LangGraph.
    Utiliza ConversationManager para la persistencia del historial.
    """
    def __init__(self):
        """Inicializa el asistente y el gestor de memoria."""
        self.memory = ConversationManager()
        logging.info("WhatsappAssistant inicializado.")

    def get_response(self, user_id: str, user_query: str) -> str:
        """Obtiene una respuesta del agente de LangGraph para un usuario y una consulta dados."""
        logging.info(f"Procesando mensaje de {user_id} con LangGraph y memoria Redis.")

        conversation_history = self.memory.get_history(user_id)
        if not conversation_history:
            conversation_history = [system_message]
            logging.info(f"Nuevo hilo de conversación para {user_id} en Redis.")
        
        current_message = HumanMessage(content=user_query)
        self.memory.add_message(user_id, current_message)
        conversation_history.append(current_message)

        graph_input = {"messages": conversation_history}
        final_response = None
        for event in app.stream(graph_input):
            if "agent" in event:
                final_response = event["agent"]["messages"][-1]
            elif "__end__" in event:
                final_response = event["__end__"]["messages"][-1]

        if not final_response:
            logging.error("El grafo de LangGraph no produjo una respuesta final.")
            return "Lo siento, tuve un problema para procesar tu mensaje."

        self.memory.add_message(user_id, final_response)
        return final_response.content

    def clear_memory(self, user_id: str):
        """Borra el historial de conversación para un usuario específico usando Redis."""
        self.memory.clear_history(user_id)
