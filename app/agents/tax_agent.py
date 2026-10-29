"""Agente especializado en regímenes tributarios peruanos (NRUS, RER, RMT, RG)."""

import re
from langchain_core.messages import HumanMessage, SystemMessage
from app.graph.state import AgentState
from app.tools.tax_tools import recommend_tax_regime, get_tax_regime_info
from app.callbacks.metrics_callback import metrics_collector, PNTEMetricsCallbackHandler
from app.core.llm import get_llm


TAX_SYSTEM_PROMPT = """Eres el asesor tributario del Programa Nacional Tu Empresa (PNTE).
Tu especialidad son los 4 regímenes tributarios peruanos: NRUS, RER, RMT y RG.
REGLAS ESTRICTAS:
- Responde con tono cordial, claro, accesible y lenguaje sencillo.
- MÁXIMO 250 CARACTERES por respuesta.
- Aclara diferencias clave: nivel de ventas, si emite facturas, libros contables e IGV."""


def tax_agent_node(state: AgentState) -> AgentState:
    """Nodo que procesa consultas sobre impuestos y regímenes tributarios."""
    metrics_collector.record_agent_call("tax_agent")
    user_msg = state["messages"][-1].content.strip()
    msg_lower = user_msg.lower()

    # Detectar si mencionan un monto de ventas (ej: "vendo 10000 al año" o "50000 soles")
    sales_match = re.search(r"(\d+[\d,\.]*)\s*(soles|mil|anual)?", msg_lower)
    if "vendo" in msg_lower or "ingresos" in msg_lower or "ventas" in msg_lower:
        raw_amount = 50000.0
        if sales_match:
            try:
                raw_amount = float(sales_match.group(1).replace(",", ""))
                if "mil" in msg_lower and raw_amount < 1000:
                    raw_amount *= 1000
            except ValueError:
                raw_amount = 50000.0

        is_juridica = any(k in msg_lower for k in ["sac", "srl", "eirl", "juridica"])
        rec = recommend_tax_regime(raw_amount, is_juridica=is_juridica)
        response_text = rec["summary"]
    else:
        # Consultar régimen específico
        detected_code = None
        for code in ["NRUS", "RER", "RMT", "RG"]:
            if code.lower() in msg_lower:
                detected_code = code
                break

        kb_tax_info = get_tax_regime_info(detected_code or "general")

        llm = get_llm(callbacks=[PNTEMetricsCallbackHandler("tax_agent")])
        if llm:
            try:
                response = llm.invoke([
                    SystemMessage(content=TAX_SYSTEM_PROMPT),
                    SystemMessage(content=f"Información tributaria oficial: {kb_tax_info}"),
                    HumanMessage(content=user_msg),
                ])
                response_text = response.content.strip()
            except Exception:
                response_text = kb_tax_info
        else:
            response_text = kb_tax_info

    return {
        **state,
        "final_response": response_text,
        "active_agent": "tax_agent",
    }
