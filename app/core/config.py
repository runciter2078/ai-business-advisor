"""
Configuración centralizada de la aplicación.

Usa pydantic-settings para leer variables de entorno y .env.
Un único objeto `settings` importable desde cualquier módulo.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- App ---
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "info"
    allowed_origins: list[str] = ["http://localhost:8501"]  # Streamlit

    # --- Base de datos ---
    database_url: str = "sqlite+aiosqlite:///./data/ai_advisor.db"

    # --- LLM ---
    openai_api_key: str = ""
    groq_api_key: str = ""
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o-mini"

    # --- Evidently ---
    drift_reports_dir: str = "./data/drift_reports"

    # --- Paths ---
    context_dir: str = "./app/context"
    data_dir: str = "./data"


settings = Settings()
