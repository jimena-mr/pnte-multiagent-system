from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración global de la aplicación."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Configuración de OpenAI y LLM
    openai_api_key: str = "mock-key-for-local-testing"
    openai_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.2

    # Guardrails y límites estrictos
    max_response_chars: int = 250
    system_scope_rejection: str = (
        "Solo puedo ayudarte con formalización y constitución de empresas. ¿Te ayudo en algo más?"
    )

    # Parámetros PNTE y Perú
    uit_value: float = 5350.0  # UIT vigente 2025
    min_capital_pen: float = 1.0
    notary_base_cost: float = 120.0

    # Base de datos y sesiones
    database_url: str = "sqlite+aiosqlite:///./pnte_database.db"
    ticket_expiry_hours: int = 24

    # API y Servidor
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"
    port: int = 8000
    host: str = "0.0.0.0"


@lru_cache()
def get_settings() -> Settings:
    """Devuelve una instancia en caché de las configuraciones."""
    return Settings()
