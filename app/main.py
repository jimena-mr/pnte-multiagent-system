"""Punto de entrada de la aplicación FastAPI para el Asistente Multiagente del PNTE."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.api.routes import router as api_router
from app.services.db_service import init_db
from app.core.logging import logger

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ciclo de vida de la aplicación: inicialización de BD y recursos."""
    logger.info("Iniciando aplicación y creando tablas en SQLite...")
    await init_db()
    logger.info("Base de datos lista. Asistente Multiagente PNTE activo.")
    yield
    logger.info("Deteniendo aplicación PNTE...")


app = FastAPI(
    title="Asistente Multiagente PNTE - Formalización de Empresas",
    description=(
        "Sistema multiagente con LangGraph, FastAPI, Guardrails y Callbacks para "
        "atender consultas sobre formalización y constitución de empresas del "
        "Programa Nacional Tu Empresa (PNTE) - Ministerio de la Producción del Perú."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# Configuración de CORS para permitir conexiones desde cualquier cliente web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar rutas con el prefijo /api/v1
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/", tags=["General"])
async def root():
    """Ruta raíz informativa con enlace a la documentación."""
    return {
        "message": "Bienvenido al Asistente Virtual Multiagente del PNTE",
        "docs_url": "/docs",
        "api_v1": f"{settings.api_v1_prefix}/chat",
        "purpose": "Formalización y constitución de empresas en Perú 24/7",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=(settings.app_env == "development"),
    )
