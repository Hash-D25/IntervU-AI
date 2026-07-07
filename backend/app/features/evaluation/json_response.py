"""Parse LLM JSON responses into answer evaluations."""

import json
from typing import Any

from app.core.exceptions import ParseError
from app.features.evaluation.schemas import AnswerEvaluationResult
from app.shared.llm_json import extract_json_payload


def parse_evaluation_response(raw_response: str) -> AnswerEvaluationResult:
    try:
        payload: dict[str, Any] = json.loads(extract_json_payload(raw_response))
        payload.setdefault("overall_score", 0.0)
        payload.setdefault("evaluator_name", "llm")
        return AnswerEvaluationResult.model_validate(payload)
    except (json.JSONDecodeError, ValueError) as exc:
        raise ParseError("LLM returned invalid evaluation JSON") from exc
