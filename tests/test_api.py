"""Pruebas de integración HTTP de la API FastAPI."""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
@pytest.mark.asyncio
async def test_root_endpoint():
    """Verifica el endpoint raíz informativo."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "PNTE" in data["message"]
        assert data["docs_url"] == "/docs"


@pytest.mark.asyncio
async def test_health_endpoint():
    """Verifica el endpoint de salud."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "LangGraph" in data["framework"]


@pytest.mark.asyncio
async def test_chat_endpoint_valid():
    """Verifica el endpoint conversacional principal."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "session_id": "test_api_session_01",
            "message": "¿Cuáles son las ventajas de formalizar mi negocio como SAC?",
            "channel": "web",
        }
        response = await client.post("/api/v1/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert len(data["response"]) <= 250
        assert data["character_count"] == len(data["response"])
        assert data["agent_used"] in ["formalization_agent", "supervisor"]


@pytest.mark.asyncio
async def test_chat_endpoint_out_of_scope():
    """Verifica la respuesta para consultas fuera de alcance por API."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "session_id": "test_api_session_02",
            "message": "¿Cuáles son las mejores playas para surfear en Lima?",
            "channel": "web",
        }
        response = await client.post("/api/v1/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["response"] == "Solo puedo ayudarte con formalización y constitución de empresas. ¿Te ayudo en algo más?"
        assert "out_of_scope_replaced" in data["guardrails_applied"]


@pytest.mark.asyncio
async def test_metrics_endpoint():
    """Verifica que el endpoint de métricas devuelva estadísticas válidas."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "total_requests" in data
        assert "latency_ms" in data
        assert "agent_invocations" in data


@pytest.mark.asyncio
async def test_advisor_requests_endpoint():
    """Verifica que el endpoint devuelva las solicitudes de asesores."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/advisor-requests")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.asyncio
async def test_chat_stream_endpoint():
    """Verifica el endpoint de streaming SSE."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "session_id": "test_api_stream_01",
            "message": "¿Dónde queda la sede de Lima?",
        }
        response = await client.post("/api/v1/chat/stream", json=payload)
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]
        body = response.text
        assert "data:" in body
        assert "[DONE]" in body
