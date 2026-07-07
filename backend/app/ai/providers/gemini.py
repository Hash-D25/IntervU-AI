"""Google Gemini LLM provider (REST API via httpx)."""

from collections.abc import Sequence

import httpx

from app.ai.providers.base import ChatMessage
from app.core.exceptions import BadRequestError

_GEMINI_API = "https://generativelanguage.googleapis.com/v1beta/models"


class GeminiLLMProvider:
    def __init__(self, *, api_key: str, model: str) -> None:
        if not api_key or api_key == "changeme":
            raise BadRequestError("LLM_API_KEY is required for Gemini")
        self._api_key = api_key
        self._model = model
        self._client = httpx.AsyncClient(timeout=120.0)

    async def generate(self, messages: Sequence[ChatMessage]) -> str:
        prompt = self._format_messages(messages)
        url = f"{_GEMINI_API}/{self._model}:generateContent"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "application/json"},
        }
        response = await self._client.post(url, params={"key": self._api_key}, json=payload)
        if response.status_code >= 400:
            raise BadRequestError(f"Gemini request failed: {response.text[:200]}")
        data = response.json()
        return self._extract_text(data)

    @staticmethod
    def _format_messages(messages: Sequence[ChatMessage]) -> str:
        return "\n\n".join(f"{message.role.upper()}:\n{message.content}" for message in messages)

    @staticmethod
    def _extract_text(data: dict[str, object]) -> str:
        candidates = data.get("candidates")
        if not isinstance(candidates, list) or not candidates:
            return ""
        first = candidates[0]
        if not isinstance(first, dict):
            return ""
        content = first.get("content")
        if not isinstance(content, dict):
            return ""
        parts = content.get("parts")
        if not isinstance(parts, list):
            return ""
        texts: list[str] = []
        for part in parts:
            if isinstance(part, dict) and isinstance(part.get("text"), str):
                texts.append(part["text"])
        return "\n".join(texts)
