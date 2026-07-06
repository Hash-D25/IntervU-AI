"""Typed application configuration loaded from environment variables.

Nothing in the app reads ``os.environ`` directly; everything goes through
``Settings`` so configuration is validated once and injected via DI.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    app_env: str = "development"
    log_level: str = "INFO"
    api_v1_prefix: str = "/api/v1"

    # Database (async psycopg driver, e.g. postgresql+psycopg://...)
    database_url: str

    # Authentication / JWT. Override JWT_SECRET_KEY in every real environment.
    jwt_secret_key: str = "dev-insecure-secret-change-me-in-every-real-environment"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # LLM provider (OpenAI-compatible). Values are read now but only consumed
    # once AI features land in a later iteration.
    llm_provider: str = "openai"
    llm_api_key: str = "changeme"
    llm_base_url: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-4o-mini"

    # Vector store
    chroma_host: str = "localhost"
    chroma_port: int = 8001

    # Voice / transcription
    whisper_model: str = "base"


@lru_cache
def get_settings() -> Settings:
    """Return a cached ``Settings`` instance (one load per process)."""
    return Settings()
