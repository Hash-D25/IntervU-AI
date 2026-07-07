"""Post-generation validation and normalization."""

import re

from app.core.exceptions import ParseError
from app.features.interview.question_generation.schemas import GeneratedQuestion

_MAX_TOPICS = 8
_MAX_RUBRIC_ITEMS = 8
_MULTI_SPACE = re.compile(r"\s+")


class GeneratedQuestionValidator:
    @classmethod
    def validate(cls, question: GeneratedQuestion) -> GeneratedQuestion:
        cls._ensure_limits(question)
        return GeneratedQuestion(
            text=_MULTI_SPACE.sub(" ", question.text.strip()),
            category=question.category,
            expected_topics=_normalize_list(question.expected_topics),
            difficulty=question.difficulty,
            evaluation_rubric=_normalize_list(question.evaluation_rubric),
        )

    @classmethod
    def _ensure_limits(cls, question: GeneratedQuestion) -> None:
        if len(question.expected_topics) > _MAX_TOPICS:
            raise ParseError("Generated question has too many expected topics")
        if len(question.evaluation_rubric) > _MAX_RUBRIC_ITEMS:
            raise ParseError("Generated question has too many rubric items")


def _normalize_list(values: list[str]) -> list[str]:
    seen: set[str] = set()
    normalized: list[str] = []
    for value in values:
        item = _MULTI_SPACE.sub(" ", value.strip())
        if not item:
            continue
        key = item.casefold()
        if key in seen:
            continue
        seen.add(key)
        normalized.append(item)
    return normalized
