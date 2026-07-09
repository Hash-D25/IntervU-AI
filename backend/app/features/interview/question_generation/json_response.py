"""Parse LLM JSON responses into generated questions."""

from typing import Any

from app.features.interview.question_generation.schemas import GeneratedQuestion, QuestionCategory
from app.shared.llm_json import parse_llm_payload


def parse_question_response(raw_response: str, category: QuestionCategory) -> GeneratedQuestion:
    def preprocess(payload: dict[str, Any]) -> None:
        payload["category"] = category.value

    return parse_llm_payload(
        raw_response,
        GeneratedQuestion,
        error_message="LLM returned invalid question JSON",
        preprocess=preprocess,
    )
