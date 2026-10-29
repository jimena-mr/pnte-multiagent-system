"""Rutas y controladores FastAPI para el asistente virtual del PNTE."""

from typing import List
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.api.schemas import (
    ChatRequest,
    ChatResponse,
    AdvisorTicketResponse,
    MetricsResponse,
    HealthResponse,
)
from app.services.chat_service import process_chat_message, stream_chat_message
from app.services.db_service import get_advisor_tickets
from app.callbacks.metrics_callback import metrics_collector

router = APIRouter()


@router.post("/chat", response_model=ChatResponse, summary="Enviar consulta al asistente")
async def chat_endpoint(request: ChatRequest):
    """Procesa una consulta mediante el sistema multiagente con LangGraph."""
    try:
        user_metadata = {}
        if request.phone:
            user_metadata["phone"] = request.phone

        result = await process_chat_message(
            session_id=request.session_id,
            message=request.message,
            user_metadata=user_metadata,
        )
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar consulta: {str(e)}")


@router.post("/chat/stream", summary="Streaming SSE de respuesta")
async def chat_stream_endpoint(request: ChatRequest):
    """Envía la respuesta en tiempo real a través de Server-Sent Events (SSE)."""
    user_metadata = {}
    if request.phone:
        user_metadata["phone"] = request.phone

    return StreamingResponse(
        stream_chat_message(
            session_id=request.session_id,
            message=request.message,
            user_metadata=user_metadata,
        ),
        media_type="text/event-stream",
    )


@router.get(
    "/advisor-requests",
    response_model=List[AdvisorTicketResponse],
    summary="Listar solicitudes con asesores",
)
async def list_advisor_requests(limit: int = 50):
    """Obtiene los tickets registrados para contacto con asesores empresariales."""
    tickets = await get_advisor_tickets(limit=limit)
    return [AdvisorTicketResponse(**t) for t in tickets]


@router.get("/metrics", response_model=MetricsResponse, summary="Métricas de observabilidad")
async def get_system_metrics():
    """Retorna métricas de latencia, tokens y llamadas a agentes."""
    return MetricsResponse(**metrics_collector.get_summary())


@router.get("/health", response_model=HealthResponse, summary="Verificación de estado")
async def health_check():
    """Comprueba el estado operativo del servicio."""
    return HealthResponse()
