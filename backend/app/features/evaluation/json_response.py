"""Parse LLM JSON responses into answer evaluations."""

from typing import Any

from app.features.evaluation.schemas import AnswerEvaluationResult
from app.shared.llm_json import parse_llm_payload


def _normalize_evaluation_payload(payload: dict[str, Any]) -> None:
    payload.setdefault("overall_score", 0.0)
    payload.setdefault("evaluator_name", "llm")


def parse_evaluation_response(raw_response: str) -> AnswerEvaluationResult:
    return parse_llm_payload(
        raw_response,
        AnswerEvaluationResult,
        error_message="LLM returned invalid evaluation JSON",
        preprocess=_normalize_evaluation_payload,
    )
