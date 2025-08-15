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


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], lambda x, y: x + y]

tools = [
    get_knowledge_base_response, 
    add_item_to_cart, 
    view_cart, 
    checkout, 
    talk_to_human
]

tool_node = ToolNode(tools)

model = ChatOpenAI(model="gpt-4o-mini", temperature=0, streaming=True)
model_with_tools = model.bind_tools(tools)

def should_continue(state: AgentState) -> str:
    """Decide si continuar llamando herramientas o finalizar el flujo."""
    last_message = state['messages'][-1]
    if not last_message.tool_calls:
        return "end"
    return "continue"

def call_model(state: AgentState) -> dict:
    """El nodo principal del agente: llama al LLM para decidir el próximo paso."""
    messages = state['messages']
    response = model_with_tools.invoke(messages)
    return {"messages": [response]}


workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("action", tool_node)

workflow.set_entry_point("agent")
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "action",
        "end": END,
    },
)

workflow.add_edge("action", "agent")

app = workflow.compile()

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
