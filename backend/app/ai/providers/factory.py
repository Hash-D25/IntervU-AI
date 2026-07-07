"""Select an LLM provider implementation from configuration."""

from dataclasses import dataclass

from app.ai.providers.base import LLMProvider
from app.ai.providers.fallback import FallbackLLMProvider
from app.ai.providers.gemini import GeminiLLMProvider
from app.ai.providers.openai_compatible import OpenAICompatibleLLMProvider
from app.core.config import Settings
from app.core.exceptions import BadRequestError

_OPENAI_COMPATIBLE = frozenset({"openai", "groq", "ollama"})
_JSON_MODE = frozenset({"openai", "groq"})


@dataclass(frozen=True, slots=True)
class _ProviderConfig:
    name: str
    api_key: str
    base_url: str
    model: str


def create_llm_provider(settings: Settings) -> LLMProvider:
    primary = _create_named_provider(_primary_config(settings), settings)
    fallback_name = settings.llm_fallback_provider.strip().lower()
    if not fallback_name:
        return primary
    fallback = _create_named_provider(_fallback_config(settings, fallback_name), settings)
    return FallbackLLMProvider(
        primary,
        fallback,
        primary_name=settings.llm_provider.strip().lower(),
        fallback_name=fallback_name,
        primary_timeout_seconds=settings.llm_primary_timeout_seconds,
    )


def _primary_config(settings: Settings) -> _ProviderConfig:
    return _ProviderConfig(
        name=settings.llm_provider.strip().lower(),
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        model=settings.llm_model,
    )


def _fallback_config(settings: Settings, name: str) -> _ProviderConfig:
    return _ProviderConfig(
        name=name,
        api_key=settings.llm_fallback_api_key,
        base_url=settings.llm_fallback_base_url,
        model=settings.llm_fallback_model,
    )


def _create_named_provider(config: _ProviderConfig, settings: Settings) -> LLMProvider:
    if config.name in _OPENAI_COMPATIBLE:
        extra_body = _ollama_extra_body(settings) if config.name == "ollama" else None
        return OpenAICompatibleLLMProvider(
            api_key=config.api_key,
            base_url=config.base_url,
            model=config.model,
            supports_json_mode=config.name in _JSON_MODE,
            extra_body=extra_body,
            provider_name=config.name,
        )
    if config.name == "gemini":
        return GeminiLLMProvider(
            api_key=config.api_key,
            model=config.model,
        )
    raise BadRequestError(f"Unsupported LLM provider: {config.name}")


def _ollama_extra_body(settings: Settings) -> dict[str, object]:
    return {
        "keep_alive": "30m",
        "options": {
            "temperature": 0,
            "num_predict": settings.llm_num_predict,
            "top_p": 0.9,
            "num_ctx": 4096,
        },
    }
