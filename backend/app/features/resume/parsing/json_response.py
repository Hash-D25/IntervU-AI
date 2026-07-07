"""Shared helpers for parsing LLM JSON resume responses."""

import json
import re
from typing import Any

from app.core.exceptions import ParseError
from app.features.resume.parsing.schemas import ParsedResume

# Qwen3 and similar models wrap reasoning in XML-style thinking blocks.
_THINKING_BLOCK = re.compile(
    r"<\s*think(?:ing)?\s*>[\s\S]*?<\s*/\s*think(?:ing)?\s*>",
    re.IGNORECASE,
)


def parse_llm_json_response(raw_response: str) -> ParsedResume:
    try:
        payload: dict[str, Any] = json.loads(extract_json_payload(raw_response))
        return ParsedResume.model_validate(payload)
    except (json.JSONDecodeError, ValueError) as exc:
        raise ParseError("LLM returned invalid resume JSON") from exc


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
