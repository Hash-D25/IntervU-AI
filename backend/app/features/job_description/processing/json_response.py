"""Parse LLM JSON responses into structured job description output."""

import json
from typing import Any

from app.core.exceptions import ParseError
from app.features.job_description.processing.schemas import ParsedJobDescription
from app.shared.llm_json import extract_json_payload


def parse_llm_json_response(raw_response: str) -> ParsedJobDescription:
    try:
        payload: dict[str, Any] = json.loads(extract_json_payload(raw_response))
        return ParsedJobDescription.model_validate(payload)
    except (json.JSONDecodeError, ValueError) as exc:
        raise ParseError("LLM returned invalid job description JSON") from exc
