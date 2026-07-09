"""Parse LLM JSON responses into feedback results."""

from typing import Any

from app.features.feedback.schemas import FeedbackResult
from app.shared.llm_json import parse_llm_payload


def _normalize_feedback_payload(payload: dict[str, Any]) -> None:
    if "roadmap" in payload and "learning_roadmap" not in payload:
        payload["learning_roadmap"] = payload.pop("roadmap")
    payload.setdefault("overall_score", 0.0)
    payload.setdefault("generator_name", "llm")


def parse_feedback_response(raw_response: str) -> FeedbackResult:
    return parse_llm_payload(
        raw_response,
        FeedbackResult,
        error_message="LLM returned invalid feedback JSON",
        preprocess=_normalize_feedback_payload,
    )
