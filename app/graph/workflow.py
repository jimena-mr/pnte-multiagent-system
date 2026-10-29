"""Construcción y compilación del flujo multiagente con LangGraph."""

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from app.graph.state import AgentState
from app.agents.supervisor import supervisor_node
from app.agents.greeting_agent import greeting_agent_node
from app.agents.formalization_agent import formalization_agent_node
from app.agents.tax_agent import tax_agent_node
from app.agents.cost_agent import cost_agent_node
from app.agents.escalation_agent import escalation_agent_node
from app.agents.guardrail_node import guardrail_node


def route_supervisor(state: AgentState) -> str:
    """Función de enrutamiento condicional desde el supervisor."""
    agent = state.get("active_agent", "formalization_agent")
    if agent in [
        "greeting_agent",
        "formalization_agent",
        "tax_agent",
        "cost_agent",
        "escalation_agent",
        "guardrail_node",
    ]:
        return agent
    return "formalization_agent"


def build_pnte_graph():
    """Construye y compila el grafo multiagente con persistencia en memoria."""
    builder = StateGraph(AgentState)

    # 1. Registrar nodos
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("greeting_agent", greeting_agent_node)
    builder.add_node("formalization_agent", formalization_agent_node)
    builder.add_node("tax_agent", tax_agent_node)
    builder.add_node("cost_agent", cost_agent_node)
    builder.add_node("escalation_agent", escalation_agent_node)
    builder.add_node("guardrail_node", guardrail_node)

    # 2. Conectar flujo inicial
    builder.add_edge(START, "supervisor")

    # 3. Ramificación condicional desde supervisor
    builder.add_conditional_edges(
        "supervisor",
        route_supervisor,
        {
            "greeting_agent": "greeting_agent",
            "formalization_agent": "formalization_agent",
            "tax_agent": "tax_agent",
            "cost_agent": "cost_agent",
            "escalation_agent": "escalation_agent",
            "guardrail_node": "guardrail_node",
        },
    )

    # 4. Todos los agentes especializados convergen al nodo de Guardrails
    builder.add_edge("greeting_agent", "guardrail_node")
    builder.add_edge("formalization_agent", "guardrail_node")
    builder.add_edge("tax_agent", "guardrail_node")
    builder.add_edge("cost_agent", "guardrail_node")
    builder.add_edge("escalation_agent", "guardrail_node")

    # 5. Guardrail finaliza la ejecución
    builder.add_edge("guardrail_node", END)

    # 6. Checkpointer para memoria por thread_id
    memory = MemorySaver()
    compiled_graph = builder.compile(checkpointer=memory)
    return compiled_graph


# Instancia única del grafo compilado
pnte_agent_graph = build_pnte_graph()
