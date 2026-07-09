"""Typed application configuration loaded from environment variables.

Nothing in the app reads ``os.environ`` directly; everything goes through
``Settings`` so configuration is validated once and injected via DI.
"""

from functools import lru_cache

from pydantic import field_validator
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

    # Google SSO (Google Cloud OAuth 2.0 Web client ID).
    google_client_id: str = ""

    # Resume uploads. ``local`` writes to disk; ``cloudinary`` uses Cloudinary raw uploads.
    resume_storage_backend: str = "local"
    resume_upload_dir: str = "uploads"
    resume_max_size_mb: int = 5
    resume_parser: str = "hybrid"
    cloudinary_cloud_name: str = ""
    cloudinary_api_key: str = ""
    cloudinary_api_secret: str = ""

    # LLM provider - primary (ollama | groq | gemini | openai) + optional fallback.
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
    transcriber: str = "fake"
    voice_max_size_mb: int = 25
    whisper_model: str = "base"
    whisper_language: str = ""
    whisper_device: str = "cpu"
    whisper_compute_type: str = "int8"
    enable_vad: bool = True
    max_audio_duration_seconds: int = 300
    supported_audio_formats: str = "wav,mp3,m4a,webm,ogg"
    return_word_timestamps: bool = False
    whisper_beam_size: int = 5
    transcript_refiner: str = "llm"
    follow_up_generator: str = "llm"
    max_follow_ups_per_answer: int = 1
    max_follow_ups_per_interview: int = 3
    follow_up_on_phases: str = "resume,projects,cs_fundamentals,behavioral"
    interview_memory: str = "session"
    interview_memory_max_answers: int = 8
    interview_memory_excerpt_chars: int = 280

    # Realtime voice-to-voice interview (V2). Gated by REALTIME_INTERVIEW_ENABLED.
    synthesizer: str = "fake"  # fake | browser | groq | openai | gemini | elevenlabs
    tts_voice: str = ""
    tts_model: str = ""
    tts_api_key: str = ""
    tts_base_url: str = ""
    realtime_interview_enabled: bool = False
    ws_max_session_minutes: int = 30
    turn_silence_ms: int = 1500
    turn_min_speech_ms: int = 800

    # Vector store
    chroma_host: str = "localhost"
    chroma_port: int = 8001

    # CORS - comma-separated origins for production; dev also allows localhost regex.
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000,https://interv-u-ai-orcin.vercel.app"

    @field_validator("google_client_id", mode="before")
    @classmethod
    def normalize_google_client_id(cls, value: object) -> str:
        if isinstance(value, str):
            return value.strip().strip('"').strip("'")
        return ""

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        """Accept Render/Heroku ``postgres://`` URLs for the async psycopg driver."""
        if not isinstance(value, str):
            return value
        if value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql+psycopg://", 1)
        if value.startswith("postgresql://") and "+psycopg" not in value:
            return value.replace("postgresql://", "postgresql+psycopg://", 1)
        return value

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    def validate_for_production(self) -> None:
        """Fail fast when production is misconfigured."""
        if self.app_env != "production":
            return

        insecure_default = "dev-insecure-secret-change-me-in-every-real-environment"
        if self.jwt_secret_key == insecure_default:
            raise ValueError("JWT_SECRET_KEY must be set to a strong secret in production")

        if len(self.jwt_secret_key) < 32:
            raise ValueError("JWT_SECRET_KEY must be at least 32 characters in production")


@lru_cache
def get_settings() -> Settings:
    """Return a cached ``Settings`` instance (one load per process)."""
    return Settings()
