"""Definición del estado global del grafo multiagente con LangGraph."""

from typing import Annotated, Sequence, Dict, Any, List, Optional
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """Estado compartido a lo largo del flujo del grafo multiagente."""

    messages: Annotated[Sequence[BaseMessage], add_messages]
    session_id: str
    user_data: Dict[str, Any]
    current_intent: str
    active_agent: str
    escalation_step: Optional[str]
    guardrail_flags: List[str]
    final_response: str
    in_scope: bool
