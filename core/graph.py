import logging
from typing import TypedDict, Annotated
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from core.tools import (
    get_knowledge_base_response,
    add_item_to_cart,
    view_cart,
    checkout,
    talk_to_human
)

# 1. Definir el Estado del Agente
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], lambda x, y: x + y]

# 2. Definir Herramientas y Nodos
tools = [
    get_knowledge_base_response, 
    add_item_to_cart, 
    view_cart, 
    checkout, 
    talk_to_human
]

# El ToolNode es un nodo pre-construido que ejecuta las herramientas que el LLM decida llamar
tool_node = ToolNode(tools)

# El modelo que actuará como el agente que decide qué herramienta llamar
model = ChatOpenAI(model="gpt-4o-mini", temperature=0, streaming=True)

# Vinculamos las herramientas al modelo para que sepa cuáles puede usar
model_with_tools = model.bind_tools(tools)

# 3. Definir la lógica de los Nodos y Aristas

def should_continue(state: AgentState) -> str:
    """Decide si continuar llamando herramientas o finalizar el flujo."""
    last_message = state['messages'][-1]
    # Si no hay llamadas a herramientas, finalizamos.
    if not last_message.tool_calls:
        return "end"
    # De lo contrario, continuamos llamando a las herramientas.
    return "continue"

def call_model(state: AgentState) -> dict:
    """El nodo principal del agente: llama al LLM para decidir el próximo paso."""
    messages = state['messages']
    response = model_with_tools.invoke(messages)
    # Devolvemos el estado actualizado con la respuesta del modelo
    return {"messages": [response]}

# 4. Construir el Grafo

# Creamos una nueva instancia del grafo de estado
workflow = StateGraph(AgentState)

# Añadimos los nodos al grafo
workflow.add_node("agent", call_model)
workflow.add_node("action", tool_node)

# Definimos el punto de entrada del grafo
workflow.set_entry_point("agent")

# Añadimos las aristas condicionales
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "action",
        "end": END,
    },
)

# Añadimos una arista normal desde el nodo de acción de vuelta al agente
workflow.add_edge("action", "agent")

# Compilamos el grafo para tener un objeto ejecutable
app = workflow.compile()

# Añadimos un SystemMessage para darle contexto inicial al agente
# Esto reemplaza el gran bloque de texto en el prompt anterior
system_message = SystemMessage(
    content=(
        "Eres SemillaBot, un asistente de WhatsApp para La Semilla Café. "
        "Tu personalidad es amable, servicial y un poco informal. "
        "Tu objetivo principal es ayudar a los clientes a pedir comida y responder sus preguntas sobre el café. "
        "Usa las herramientas disponibles para gestionar el carrito de compras, responder preguntas y, si es necesario, contactar a un humano. "
        "Siempre sé proactivo y servicial."
    )
)

logging.info("Grafo de LangGraph compilado y listo.")
