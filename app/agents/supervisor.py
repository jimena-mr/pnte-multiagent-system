"""Supervisor / Router Agent para clasificación de intención y delegación en LangGraph."""

from langchain_core.messages import HumanMessage, SystemMessage
from app.graph.state import AgentState
from app.guardrails.input_guardrails import validate_input
from app.callbacks.metrics_callback import metrics_collector, PNTEMetricsCallbackHandler
from app.core.llm import get_llm
from app.utils.text import normalize_text


SUPERVISOR_PROMPT = """Eres el orquestador del Programa Nacional Tu Empresa (PNTE).
Tu misión es clasificar la intención del usuario en una de las siguientes categorías exactas:
- "escalation": Si el usuario solicita hablar con un asesor humano, registrarse para una llamada o contactar al personal.
- "greeting": Si el usuario saluda ("hola", "buenos días") o pide ver el menú de opciones.
- "formalization": Si pregunta sobre tipos de empresa (EIRL, SRL, SAC, SACS, Persona Natural), requisitos, pasos, minuta, SUNARP o actividades permitidas/restringidas.
- "tax": Si consulta sobre regímenes tributarios (NRUS, RER, RMT, General), ventas anuales, IGV, libros contables o comprobantes.
- "cost": Si pregunta por costos de constitución, tarifas notariales, 1 UIT o ubicación de sedes/CDE.
- "out_of_scope": Si la consulta NO guarda ninguna relación con formalización ni creación de empresas en Perú.

Responde ÚNICAMENTE con la palabra de la categoría (sin puntuación ni explicaciones)."""


def supervisor_node(state: AgentState) -> AgentState:
    """Nodo Supervisor que clasifica y enruta la conversación."""
    metrics_collector.record_agent_call("supervisor")
    
    # 1. Si el usuario ya está en medio de un flujo de escalamiento con asesor, continuamos en él
    current_step = state.get("escalation_step")
    if current_step and current_step not in ["idle", "completed"]:
        return {
            **state,
            "current_intent": "escalation",
            "active_agent": "escalation_agent",
            "in_scope": True,
        }

    # 2. Obtener el último mensaje del usuario
    messages = state.get("messages", [])
    if not messages:
        return {
            **state,
            "current_intent": "greeting",
            "active_agent": "greeting_agent",
            "in_scope": True,
        }

    last_user_msg = messages[-1].content.strip()

    # 3. Aplicar Input Guardrail inicial
    is_safe, in_scope, reason = validate_input(last_user_msg)
    if not in_scope or not is_safe:
        metrics_collector.record_guardrail_action("out_of_scope_replaced")
        return {
            **state,
            "current_intent": "out_of_scope",
            "active_agent": "guardrail_node",
            "in_scope": False,
            "guardrail_flags": state.get("guardrail_flags", []) + [reason],
        }

    # 4. Clasificación rápida basada en patrones frecuentes
    msg_lower = normalize_text(last_user_msg)

    if any(k in msg_lower for k in ["asesor", "persona humana", "humano", "contactar con un asesor", "opcion 5", "5"]):
        return {
            **state,
            "current_intent": "escalation",
            "active_agent": "escalation_agent",
            "in_scope": True,
        }

    if any(k in msg_lower for k in ["hola", "buenos dias", "buenas tardes", "buenas noches", "menu", "inicio", "empezar"]):
        return {
            **state,
            "current_intent": "greeting",
            "active_agent": "greeting_agent",
            "in_scope": True,
        }

    if any(k in msg_lower for k in ["tributo", "tributario", "impuesto", "renta", "nrus", "rus", "rer", "rmt", "general", "igv", "factura"]):
        return {
            **state,
            "current_intent": "tax",
            "active_agent": "tax_agent",
            "in_scope": True,
        }

    if any(k in msg_lower for k in ["costo", "precio", "tarifa", "cuanto", "cobra", "notaria", "notario", "notariales", "uit", "sede", "oficina", "donde"]):
        return {
            **state,
            "current_intent": "cost",
            "active_agent": "cost_agent",
            "in_scope": True,
        }

    if any(k in msg_lower for k in ["empresa", "eirl", "srl", "sac", "sacs", "persona natural", "requisito", "minuta", "nombre", "sunarp", "socio", "capital"]):
        return {
            **state,
            "current_intent": "formalization",
            "active_agent": "formalization_agent",
            "in_scope": True,
        }

    # 5. Si hay LLM configurado, usamos razonamiento con LLM
    llm = get_llm(callbacks=[PNTEMetricsCallbackHandler("supervisor")])
    if llm:
        try:
            response = llm.invoke([
                SystemMessage(content=SUPERVISOR_PROMPT),
                HumanMessage(content=last_user_msg),
            ])
            intent = response.content.strip().lower()
            if intent in ["escalation", "greeting", "formalization", "tax", "cost", "out_of_scope"]:
                agent_map = {
                    "escalation": "escalation_agent",
                    "greeting": "greeting_agent",
                    "formalization": "formalization_agent",
                    "tax": "tax_agent",
                    "cost": "cost_agent",
                    "out_of_scope": "guardrail_node",
                }
                return {
                    **state,
                    "current_intent": intent,
                    "active_agent": agent_map[intent],
                    "in_scope": (intent != "out_of_scope"),
                }
        except Exception:
            pass

    # Fallback por defecto a formalización
    return {
        **state,
        "current_intent": "formalization",
        "active_agent": "formalization_agent",
        "in_scope": True,
    }
