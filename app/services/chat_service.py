"""Servicio central de chat para invocar el grafo de LangGraph y gestionar respuestas."""

import time
from typing import Dict, Any, AsyncGenerator, Optional
from langchain_core.messages import HumanMessage
from app.graph.workflow import pnte_agent_graph
from app.callbacks.metrics_callback import metrics_collector
from app.services.db_service import save_message_log


async def process_chat_message(
    session_id: str,
    message: str,
    user_metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Ejecuta el grafo multiagente para un mensaje de usuario."""
    start_time = time.perf_counter()
    metrics_collector.record_request()

    # Guardar mensaje del usuario en DB
    await save_message_log(session_id=session_id, role="user", content=message)

    # Configuración de ejecución con memoria para el hilo
    config = {"configurable": {"thread_id": session_id}}

    # Entrada inicial al grafo
    initial_input = {
        "messages": [HumanMessage(content=message)],
        "session_id": session_id,
        "user_data": user_metadata or {},
    }

    # Invocación del grafo compilado de LangGraph
    result_state = await pnte_agent_graph.ainvoke(initial_input, config=config)

    latency_ms = (time.perf_counter() - start_time) * 1000
    metrics_collector.record_latency(latency_ms)

    final_response = result_state.get("final_response", "")
    active_agent = result_state.get("active_agent", "supervisor")
    flags = result_state.get("guardrail_flags", [])
    step = result_state.get("escalation_step", "idle")

    # Guardar respuesta del bot en DB
    await save_message_log(
        session_id=session_id,
        role="bot",
        content=final_response,
        agent=active_agent,
    )

    return {
        "session_id": session_id,
        "response": final_response,
        "agent_used": active_agent,
        "character_count": len(final_response),
        "guardrails_applied": flags,
        "escalation_step": step,
        "latency_ms": round(latency_ms, 2),
    }


async def stream_chat_message(
    session_id: str,
    message: str,
    user_metadata: Optional[Dict[str, Any]] = None,
) -> AsyncGenerator[str, None]:
    """Generador para streaming de respuesta en eventos SSE."""
    result = await process_chat_message(session_id, message, user_metadata)
    full_text = result["response"]

    # Simular chunks fluidos para clientes web/SSE
    chunk_size = 15
    for i in range(0, len(full_text), chunk_size):
        chunk = full_text[i : i + chunk_size]
        yield f"data: {chunk}\n\n"
    
    yield "data: [DONE]\n\n"
