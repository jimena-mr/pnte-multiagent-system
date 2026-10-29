"""Nodo de post-procesamiento y guardrail final de salida."""

from langchain_core.messages import AIMessage
from app.graph.state import AgentState
from app.guardrails.output_guardrails import enforce_output_guardrails
from app.callbacks.metrics_callback import metrics_collector


def guardrail_node(state: AgentState) -> AgentState:
    """Aplica guardrails de salida: límite de 250 caracteres, tono y filtro de alcance."""
    raw_response = state.get("final_response", "")
    in_scope = state.get("in_scope", True)

    sanitized_response, flags = enforce_output_guardrails(
        response_text=raw_response,
        in_scope=in_scope,
        max_chars=250,
    )

    for flag in flags:
        metrics_collector.record_guardrail_action(flag)

    updated_flags = state.get("guardrail_flags", []) + flags

    return {
        **state,
        "final_response": sanitized_response,
        "guardrail_flags": updated_flags,
        "messages": [AIMessage(content=sanitized_response)],
    }
