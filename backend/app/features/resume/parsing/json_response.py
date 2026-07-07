"""Shared helpers for parsing LLM JSON resume responses."""

import json
from typing import Any

from app.core.exceptions import ParseError
from app.features.resume.parsing.schemas import ParsedResume
from app.shared.llm_json import extract_json_payload


def parse_llm_json_response(raw_response: str) -> ParsedResume:
    try:
        payload: dict[str, Any] = json.loads(extract_json_payload(raw_response))
        return ParsedResume.model_validate(payload)
    except (json.JSONDecodeError, ValueError) as exc:
        raise ParseError("LLM returned invalid resume JSON") from exc
