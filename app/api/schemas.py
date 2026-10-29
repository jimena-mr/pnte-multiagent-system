"""Modelos de datos y esquemas Pydantic para la API del asistente PNTE."""

import uuid
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Petición para el endpoint conversacional."""
    session_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Identificador único de sesión o número de teléfono del usuario",
    )
    message: str = Field(..., description="Mensaje o consulta del emprendedor", min_length=1)
    phone: Optional[str] = Field(None, description="Número de teléfono de contacto opcional")
    channel: Optional[str] = Field("web", description="Canal de procedencia (web, api, etc.)")


class ChatResponse(BaseModel):
    """Respuesta generada por el sistema multiagente."""
    session_id: str
    response: str = Field(..., max_length=250, description="Respuesta final garantizada ≤ 250 caracteres")
    agent_used: str = Field(..., description="Agente especializado que resolvió la consulta")
    character_count: int = Field(..., description="Cantidad exacta de caracteres devueltos")
    guardrails_applied: List[str] = Field(default_factory=list, description="Lista de guardrails activados")
    escalation_step: Optional[str] = Field(None, description="Fase del flujo con asesor humano")
    latency_ms: float = Field(..., description="Tiempo de procesamiento en milisegundos")


class AdvisorTicketResponse(BaseModel):
    """Detalle de una solicitud registrada para asesor humano."""
    id: int
    user_id: str
    document_number: Optional[str]
    name: Optional[str]
    phone: Optional[str]
    details: Optional[str]
    status: str
    created_at: str


class MetricsResponse(BaseModel):
    """Resumen de métricas de rendimiento y uso."""
    total_requests: int
    out_of_scope_rejections: int
    character_limit_trims: int
    agent_invocations: Dict[str, int]
    total_tokens: Dict[str, int]
    latency_ms: Dict[str, float]


class HealthResponse(BaseModel):
    """Estado de salud del servicio."""
    status: str = "ok"
    app: str = "PNTE Multi-Agent Assistant"
    version: str = "1.0.0"
    framework: str = "LangGraph + FastAPI"
