"""Parse LLM JSON responses into generated questions."""

import json
from typing import Any

from app.core.exceptions import ParseError
from app.features.interview.question_generation.schemas import GeneratedQuestion, QuestionCategory
from app.shared.llm_json import extract_json_payload


def parse_question_response(raw_response: str, category: QuestionCategory) -> GeneratedQuestion:
    try:
        payload: dict[str, Any] = json.loads(extract_json_payload(raw_response))
        payload["category"] = category.value
        return GeneratedQuestion.model_validate(payload)
    except (json.JSONDecodeError, ValueError) as exc:
        raise ParseError("LLM returned invalid question JSON") from exc
