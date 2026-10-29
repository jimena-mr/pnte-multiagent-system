"""Agente especializado en formalización societaria y legal del PNTE."""

from langchain_core.messages import HumanMessage, SystemMessage
from app.graph.state import AgentState
from app.tools.kb_tools import search_formalization_kb, check_restricted_activity
from app.callbacks.metrics_callback import metrics_collector, PNTEMetricsCallbackHandler
from app.core.llm import get_llm


FORMALIZATION_SYSTEM_PROMPT = """Eres el asistente del Programa Nacional Tu Empresa (PNTE) de Perú.
Tu especialidad es la formalización y constitución de empresas (EIRL, SRL, SAC, SACS, Persona Natural).
REGLAS ESTRICTAS:
- Responde con tono cordial, claro, directo y accesible.
- MÁXIMO 250 CARACTERES por respuesta.
- Si preguntan sobre actividades prohibidas (seguros, universidades, etc.), aclara las restricciones.
- Menciona que la asesoría y reserva de nombre en PNTE son gratuitas."""


def formalization_agent_node(state: AgentState) -> AgentState:
    """Nodo que procesa consultas sobre constitución de empresas."""
    metrics_collector.record_agent_call("formalization_agent")
    user_msg = state["messages"][-1].content.strip()

    # Primero verificar si la actividad que mencionan está restringida
    activity_check = check_restricted_activity(user_msg)
    if activity_check["is_restricted"] and not activity_check["allowed_in_pnte"]:
        response_text = activity_check["summary"]
    else:
        # Consultar conocimiento oficial
        kb_context = search_formalization_kb(user_msg)

        llm = get_llm(callbacks=[PNTEMetricsCallbackHandler("formalization_agent")])
        if llm:
            try:
                response = llm.invoke([
                    SystemMessage(content=FORMALIZATION_SYSTEM_PROMPT),
                    SystemMessage(content=f"Contexto oficial PNTE: {kb_context}"),
                    HumanMessage(content=user_msg),
                ])
                response_text = response.content.strip()
            except Exception:
                response_text = kb_context
        else:
            response_text = kb_context

    return {
        **state,
        "final_response": response_text,
        "active_agent": "formalization_agent",
    }
