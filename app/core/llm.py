"""Fábrica de modelos de lenguaje (LLM) con manejo de configuración y callbacks."""

from typing import List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.callbacks.base import BaseCallbackHandler
from app.config import get_settings

settings = get_settings()


def get_llm(callbacks: Optional[List[BaseCallbackHandler]] = None) -> Optional[ChatOpenAI]:
    """Obtiene una instancia de ChatOpenAI configurada."""
    api_key = settings.openai_api_key
    # Si la clave es un mock o está vacía, retornamos None para habilitar el fallback determinista
    if not api_key or api_key.startswith("mock-") or api_key == "tu_clave_de_openai_aqui":
        return None

    return ChatOpenAI(
        model=settings.openai_model,
        temperature=settings.llm_temperature,
        api_key=api_key,
        callbacks=callbacks or [],
    )
