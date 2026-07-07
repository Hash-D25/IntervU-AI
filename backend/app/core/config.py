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

    # Resume uploads. ``local`` writes to disk; ``cloudinary`` uses Cloudinary raw uploads.
    resume_storage_backend: str = "local"
    resume_upload_dir: str = "uploads"
    resume_max_size_mb: int = 5
    resume_parser: str = "hybrid"
    cloudinary_cloud_name: str = ""
    cloudinary_api_key: str = ""
    cloudinary_api_secret: str = ""

    # LLM provider — primary (ollama | groq | gemini | openai) + optional fallback.
    llm_provider: str = "ollama"
    llm_api_key: str = "ollama"
    llm_base_url: str = "http://localhost:11434/v1"
    llm_model: str = "qwen3:8b"
    llm_fallback_provider: str = "groq"
    llm_fallback_api_key: str = ""
    llm_fallback_base_url: str = "https://api.groq.com/openai/v1"
    llm_fallback_model: str = "llama-3.1-8b-instant"
    llm_max_resume_chars: int = 6000
    llm_max_jd_chars: int = 8000
    llm_num_predict: int = 800
    llm_disable_thinking: bool = True
    llm_primary_timeout_seconds: float = 15.0
    job_description_analyzer: str = "llm"
    job_description_max_size_mb: int = 5
    question_generator: str = "llm"
    answer_evaluator: str = "llm"
    feedback_generator: str = "llm"

    # Vector store
    chroma_host: str = "localhost"
    chroma_port: int = 8001

    # Voice / transcription
    whisper_model: str = "base"


@lru_cache
def get_settings() -> Settings:
    """Return a cached ``Settings`` instance (one load per process)."""
    return Settings()
