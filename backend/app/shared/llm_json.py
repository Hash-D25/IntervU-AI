"""Shared helpers for extracting JSON from LLM text responses."""

import json
import re
from collections.abc import Callable
from typing import Any, TypeVar

from pydantic import BaseModel

from app.core.exceptions import ParseError

# Qwen3 and similar models wrap reasoning in XML-style thinking blocks.
_THINKING_BLOCK = re.compile(
    r"<\s*think(?:ing)?\s*>[\s\S]*?<\s*/\s*think(?:ing)?\s*>",
    re.IGNORECASE,
)

TModel = TypeVar("TModel", bound=BaseModel)


def extract_json_payload(raw_response: str) -> str:
    text = _THINKING_BLOCK.sub("", raw_response.strip())
    text = strip_code_fence(text)
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1]
    return text


def strip_code_fence(raw_response: str) -> str:
    text = raw_response.strip()
    if not text.startswith("```"):
        return text
    lines = text.splitlines()
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].startswith("```"):
        lines = lines[:-1]
    return "\n".join(lines).strip()


def parse_llm_payload(
    raw_response: str,
    model: type[TModel],
    *,
    error_message: str,
    preprocess: Callable[[dict[str, Any]], None] | None = None,
) -> TModel:
    """Parse an LLM text response into a validated Pydantic model."""
    try:
        payload: dict[str, Any] = json.loads(extract_json_payload(raw_response))
        if preprocess is not None:
            preprocess(payload)
        return model.model_validate(payload)
    except (json.JSONDecodeError, ValueError) as exc:
        raise ParseError(error_message) from exc
