"""LLM provider factory unit tests."""

import asyncio

import pytest

from app.ai.providers.base import ChatMessage
from app.ai.providers.factory import create_llm_provider
from app.ai.providers.fallback import FallbackLLMProvider
from app.ai.providers.gemini import GeminiLLMProvider
from app.ai.providers.openai_compatible import OpenAICompatibleLLMProvider
from app.core.config import Settings
from app.core.exceptions import BadRequestError


def _settings(**overrides: object) -> Settings:
    base = {
        "database_url": "postgresql+psycopg://u:p@localhost/db",
        "llm_fallback_provider": "",
        **overrides,
    }
    return Settings(**base)  # type: ignore[arg-type]


def test_factory_creates_ollama_provider_without_json_mode() -> None:
    provider = create_llm_provider(_settings(llm_provider="ollama"))
    assert isinstance(provider, OpenAICompatibleLLMProvider)
    assert provider._supports_json_mode is False


def test_factory_creates_groq_provider_with_json_mode() -> None:
    provider = create_llm_provider(
        _settings(
            llm_provider="groq",
            llm_base_url="https://api.groq.com/openai/v1",
            llm_api_key="gsk_test",
            llm_model="llama-3.1-8b-instant",
        )
    )
    assert isinstance(provider, OpenAICompatibleLLMProvider)
    assert provider._supports_json_mode is True


def test_factory_creates_gemini_provider() -> None:
    provider = create_llm_provider(
        _settings(llm_provider="gemini", llm_api_key="AIza-test", llm_model="gemini-2.0-flash")
    )
    assert isinstance(provider, GeminiLLMProvider)


def test_factory_wraps_fallback_when_configured() -> None:
    provider = create_llm_provider(
        _settings(
            llm_provider="ollama",
            llm_fallback_provider="groq",
            llm_fallback_api_key="gsk_test",
        )
    )
    assert isinstance(provider, FallbackLLMProvider)


async def test_fallback_provider_uses_secondary_on_primary_failure() -> None:
    class _FailingPrimary:
        async def generate(self, messages: list[ChatMessage]) -> str:
            raise ConnectionError("ollama down")

    class _WorkingFallback:
        async def generate(self, messages: list[ChatMessage]) -> str:
            return '{"skills": ["Python"]}'

    provider = FallbackLLMProvider(
        _FailingPrimary(),  # type: ignore[arg-type]
        _WorkingFallback(),  # type: ignore[arg-type]
        primary_name="ollama",
        fallback_name="groq",
    )
    result = await provider.generate([ChatMessage(role="user", content="test")])
    assert "Python" in result


async def test_fallback_provider_times_out_slow_primary() -> None:
    class _SlowPrimary:
        async def generate(self, messages: list[ChatMessage]) -> str:
            await asyncio.sleep(5)
            return "too late"

    class _WorkingFallback:
        async def generate(self, messages: list[ChatMessage]) -> str:
            return '{"skills": ["Fast"]}'

    provider = FallbackLLMProvider(
        _SlowPrimary(),  # type: ignore[arg-type]
        _WorkingFallback(),  # type: ignore[arg-type]
        primary_name="ollama",
        fallback_name="groq",
        primary_timeout_seconds=0.1,
    )
    result = await provider.generate([ChatMessage(role="user", content="test")])
    assert "Fast" in result


def test_factory_rejects_unknown_provider() -> None:
    with pytest.raises(BadRequestError, match="Unsupported LLM provider"):
        create_llm_provider(_settings(llm_provider="unknown"))
