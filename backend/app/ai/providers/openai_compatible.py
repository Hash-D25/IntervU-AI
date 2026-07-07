"""OpenAI-compatible LLM provider implementation."""

from collections.abc import Mapping, Sequence
from typing import Any, cast

import httpx
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam

from app.ai.providers.base import ChatMessage

_OLLAMA_TIMEOUT = httpx.Timeout(90.0, connect=5.0)


class OpenAICompatibleLLMProvider:
    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        model: str,
        supports_json_mode: bool = True,
        extra_body: Mapping[str, Any] | None = None,
        provider_name: str = "openai",
    ) -> None:
        client_kwargs: dict[str, Any] = {}
        if provider_name == "ollama":
            client_kwargs["max_retries"] = 0
            client_kwargs["timeout"] = _OLLAMA_TIMEOUT
        self._client = AsyncOpenAI(api_key=api_key, base_url=base_url, **client_kwargs)
        self._model = model
        self._supports_json_mode = supports_json_mode
        self._extra_body = dict(extra_body) if extra_body else None

    async def generate(self, messages: Sequence[ChatMessage]) -> str:
        payload = cast(
            list[ChatCompletionMessageParam],
            [{"role": message.role, "content": message.content} for message in messages],
        )
        kwargs: dict[str, Any] = {}
        if self._extra_body:
            kwargs["extra_body"] = self._extra_body
        if self._supports_json_mode:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=payload,
                response_format={"type": "json_object"},
                **kwargs,
            )
        else:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=payload,
                **kwargs,
            )
        content = response.choices[0].message.content
        return content if content is not None else ""
