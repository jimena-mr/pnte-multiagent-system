"""Agente de bienvenida y menú de opciones iniciales del PNTE."""

from app.graph.state import AgentState
from app.callbacks.metrics_callback import metrics_collector


def greeting_agent_node(state: AgentState) -> AgentState:
    """Nodo que presenta el saludo oficial y las opciones del PNTE."""
    metrics_collector.record_agent_call("greeting_agent")
    
    greeting_text = (
        "¡Hola! 👋 Soy el asistente virtual del PNTE para formalizar tu negocio. "
        "Pregúntame sobre: 1.Tipos de empresa (EIRL, SAC, SACS) 2.Costos y trámites "
        "3.Regímenes tributarios (NRUS/RER) o 4.Contactar con un asesor humano."
    )

    return {
        **state,
        "final_response": greeting_text[:250],
        "active_agent": "greeting_agent",
    }
