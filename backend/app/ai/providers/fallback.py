"""LLM provider that tries a primary backend, then falls back on failure."""

import asyncio
from collections.abc import Sequence

import structlog
from openai import APIConnectionError, APIStatusError, RateLimitError

from app.ai.providers.base import ChatMessage, LLMProvider
from app.core.exceptions import BadRequestError

logger = structlog.get_logger(__name__)

_FALLBACK_ERRORS = (
    APIConnectionError,
    RateLimitError,
    APIStatusError,
    BadRequestError,
    OSError,
    asyncio.TimeoutError,
)


class FallbackLLMProvider:
    def __init__(
        self,
        primary: LLMProvider,
        fallback: LLMProvider,
        *,
        primary_name: str,
        fallback_name: str,
        primary_timeout_seconds: float | None = None,
    ) -> None:
        self._primary = primary
        self._fallback = fallback
        self._primary_name = primary_name
        self._fallback_name = fallback_name
        self._primary_timeout = primary_timeout_seconds

    async def generate(self, messages: Sequence[ChatMessage]) -> str:
        try:
            if self._primary_timeout is not None:
                return await asyncio.wait_for(
                    self._primary.generate(messages),
                    timeout=self._primary_timeout,
                )
            return await self._primary.generate(messages)
        except _FALLBACK_ERRORS as exc:
            logger.warning(
                "llm_primary_failed_trying_fallback",
                primary=self._primary_name,
                fallback=self._fallback_name,
                error=str(exc),
            )
            return await self._fallback.generate(messages)
