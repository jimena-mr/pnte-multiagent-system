"""Agente especializado en costos notariales, exoneraciones y sedes del PNTE."""

import re
from langchain_core.messages import HumanMessage, SystemMessage
from app.graph.state import AgentState
from app.tools.cost_tools import calculate_constitution_costs, get_pnte_office
from app.callbacks.metrics_callback import metrics_collector, PNTEMetricsCallbackHandler
from app.core.llm import get_llm


COST_SYSTEM_PROMPT = """Eres el especialista en costos y sedes del Programa Nacional Tu Empresa (PNTE).
REGLAS ESTRICTAS:
- Responde con tono cordial, directo y accesible.
- MÁXIMO 250 CARACTERES por respuesta.
- Aclara que asesoría y reserva son GRATIS. Notaría desde S/120.
- Si el capital no supera 1 UIT (S/ 5,350), los registros públicos están exonerados."""


def cost_agent_node(state: AgentState) -> AgentState:
    """Nodo que procesa consultas sobre costos de constitución o sedes."""
    metrics_collector.record_agent_call("cost_agent")
    user_msg = state["messages"][-1].content.strip()
    msg_lower = user_msg.lower()

    # Si preguntan por sedes o lugares de atención
    if any(k in msg_lower for k in ["sede", "oficina", "donde", "cde", "direccion", "lugar", "lima", "arequipa", "piura", "cusco", "trujillo"]):
        detected_region = "lima"
        for reg in ["lima", "arequipa", "piura", "la libertad", "cusco"]:
            if reg in msg_lower:
                detected_region = reg
                break
        response_text = get_pnte_office(detected_region)
    else:
        # Consulta de costos
        capital = 1000.0
        cap_match = re.search(r"(\d+[\d,\.]*)\s*(soles|capital)?", msg_lower)
        if cap_match:
            try:
                capital = float(cap_match.group(1).replace(",", ""))
            except ValueError:
                capital = 1000.0

        calc_info = calculate_constitution_costs(capital_pen=capital)

        llm = get_llm(callbacks=[PNTEMetricsCallbackHandler("cost_agent")])
        if llm:
            try:
                response = llm.invoke([
                    SystemMessage(content=COST_SYSTEM_PROMPT),
                    SystemMessage(content=f"Datos oficiales de costos: {calc_info['summary']}"),
                    HumanMessage(content=user_msg),
                ])
                response_text = response.content.strip()
            except Exception:
                response_text = calc_info["summary"]
        else:
            response_text = calc_info["summary"]

    return {
        **state,
        "final_response": response_text,
        "active_agent": "cost_agent",
    }
