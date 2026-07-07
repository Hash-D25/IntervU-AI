"""Parse LLM JSON responses into feedback results."""

import json
from typing import Any

from app.core.exceptions import ParseError
from app.features.feedback.schemas import FeedbackResult
from app.shared.llm_json import extract_json_payload


def parse_feedback_response(raw_response: str) -> FeedbackResult:
    try:
        payload: dict[str, Any] = json.loads(extract_json_payload(raw_response))
        if "roadmap" in payload and "learning_roadmap" not in payload:
            payload["learning_roadmap"] = payload.pop("roadmap")
        payload.setdefault("overall_score", 0.0)
        payload.setdefault("generator_name", "llm")
        return FeedbackResult.model_validate(payload)
    except (json.JSONDecodeError, ValueError) as exc:
        raise ParseError("LLM returned invalid feedback JSON") from exc
