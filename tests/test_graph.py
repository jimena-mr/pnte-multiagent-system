"""Pruebas de integración del grafo multiagente con LangGraph."""

import pytest
from langchain_core.messages import HumanMessage
from app.graph.workflow import pnte_agent_graph
from app.services.db_service import init_db, get_advisor_tickets
from app.config import get_settings

settings = get_settings()


@pytest.mark.asyncio
async def test_graph_greeting_flow():
    """Valida la respuesta del nodo de saludo y opciones."""
    await init_db()
    session_id = "test_greeting_session"
    config = {"configurable": {"thread_id": session_id}}

    state = {
        "messages": [HumanMessage(content="Hola, buenos días")],
        "session_id": session_id,
        "user_data": {},
    }
    result = await pnte_agent_graph.ainvoke(state, config=config)

    assert result["active_agent"] == "greeting_agent"
    assert len(result["final_response"]) <= 250
    assert "PNTE" in result["final_response"]


@pytest.mark.asyncio
async def test_graph_formalization_flow():
    """Valida el enrutamiento y respuesta del agente de formalización."""
    await init_db()
    session_id = "test_formalization_session"
    config = {"configurable": {"thread_id": session_id}}

    state = {
        "messages": [HumanMessage(content="¿Cómo constituyo una EIRL y qué requisitos piden?")],
        "session_id": session_id,
        "user_data": {},
    }
    result = await pnte_agent_graph.ainvoke(state, config=config)

    assert result["active_agent"] == "formalization_agent"
    assert len(result["final_response"]) <= 250
    assert any(term in result["final_response"] for term in ["EIRL", "formaliza", "Requisitos", "PNTE"])


@pytest.mark.asyncio
async def test_graph_tax_flow():
    """Valida el agente tributario."""
    await init_db()
    session_id = "test_tax_session"
    config = {"configurable": {"thread_id": session_id}}

    state = {
        "messages": [HumanMessage(content="¿Cuánto se paga de impuesto en el RER mensual?")],
        "session_id": session_id,
        "user_data": {},
    }
    result = await pnte_agent_graph.ainvoke(state, config=config)

    assert result["active_agent"] == "tax_agent"
    assert len(result["final_response"]) <= 250
    assert "RER" in result["final_response"] or "1.5%" in result["final_response"]


@pytest.mark.asyncio
async def test_graph_cost_flow():
    """Valida el agente de costos notariales y sedes."""
    await init_db()
    session_id = "test_cost_session"
    config = {"configurable": {"thread_id": session_id}}

    state = {
        "messages": [HumanMessage(content="¿Cuánto cobra la notaría si tengo un capital de 2000 soles?")],
        "session_id": session_id,
        "user_data": {},
    }
    result = await pnte_agent_graph.ainvoke(state, config=config)

    assert result["active_agent"] == "cost_agent"
    assert len(result["final_response"]) <= 250
    assert "120" in result["final_response"] or "GRATIS" in result["final_response"]


@pytest.mark.asyncio
async def test_graph_out_of_scope_guardrail():
    """Valida que una consulta no relacionada sea interceptada por el guardrail."""
    await init_db()
    session_id = "test_out_of_scope_session"
    config = {"configurable": {"thread_id": session_id}}

    state = {
        "messages": [HumanMessage(content="¿Cómo se prepara el lomo saltado con papas fritas?")],
        "session_id": session_id,
        "user_data": {},
    }
    result = await pnte_agent_graph.ainvoke(state, config=config)

    assert result["final_response"] == settings.system_scope_rejection
    assert len(result["final_response"]) <= 250
    assert "out_of_scope_replaced" in result["guardrail_flags"]


@pytest.mark.asyncio
async def test_graph_escalation_full_cycle():
    """Valida el flujo conversacional paso a paso para agendar cita con asesor."""
    await init_db()
    session_id = "test_escalation_flow_01"
    config = {"configurable": {"thread_id": session_id}}

    # Paso 1: Pide asesor
    r1 = await pnte_agent_graph.ainvoke(
        {"messages": [HumanMessage(content="Quiero hablar con un asesor")], "session_id": session_id, "user_data": {}},
        config=config,
    )
    assert "documento" in r1["final_response"].lower()
    assert r1["escalation_step"] == "asking_doc"

    # Paso 2: Envía DNI
    r2 = await pnte_agent_graph.ainvoke(
        {"messages": [HumanMessage(content="76543210")], "session_id": session_id, "user_data": r1["user_data"]},
        config=config,
    )
    assert "76543210" in r2["final_response"]
    assert r2["escalation_step"] == "confirming_doc"

    # Paso 3: Confirma DNI con 'si'
    r3 = await pnte_agent_graph.ainvoke(
        {"messages": [HumanMessage(content="si")], "session_id": session_id, "user_data": r2["user_data"]},
        config=config,
    )
    assert "nombre" in r3["final_response"].lower()
    assert r3["escalation_step"] == "asking_name"

    # Paso 4: Envía nombre
    r4 = await pnte_agent_graph.ainvoke(
        {"messages": [HumanMessage(content="Rosa Perez")], "session_id": session_id, "user_data": r3["user_data"]},
        config=config,
    )
    assert "Rosa Perez" in r4["final_response"]
    assert r4["escalation_step"] == "confirming_name"

    # Paso 5: Confirma nombre con 'si'
    r5 = await pnte_agent_graph.ainvoke(
        {"messages": [HumanMessage(content="si")], "session_id": session_id, "user_data": r4["user_data"]},
        config=config,
    )
    assert "motivo" in r5["final_response"].lower()
    assert r5["escalation_step"] == "asking_motive"

    # Paso 6: Envía motivo -> se crea el ticket
    r6 = await pnte_agent_graph.ainvoke(
        {"messages": [HumanMessage(content="Quiero formalizar una panadería artesanal")], "session_id": session_id, "user_data": r5["user_data"]},
        config=config,
    )
    assert "registrada" in r6["final_response"].lower() or "anotada" in r6["final_response"].lower()
    assert r6["escalation_step"] == "completed"

    # Verificar que el ticket exista en SQLite
    tickets = await get_advisor_tickets(limit=10)
    matching = [t for t in tickets if t["document_number"] == "76543210"]
    assert len(matching) > 0
    assert matching[0]["name"] == "Rosa Perez"
