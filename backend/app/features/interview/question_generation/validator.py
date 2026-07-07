"""Post-generation validation and normalization."""

import re

from app.core.exceptions import ParseError
from app.features.interview.question_generation.schemas import (
    GeneratedQuestion,
    QuestionCategory,
    QuestionGenerationContext,
)
from app.features.resume.parsing.project_names import (
    normalize_project_references_in_text,
    sanitize_project_name,
)

_MAX_TOPICS = 8
_MAX_RUBRIC_ITEMS = 8
_MULTI_SPACE = re.compile(r"\s+")

_DEFAULT_RUBRIC: dict[QuestionCategory, list[str]] = {
    QuestionCategory.PROJECT: [
        "clarity",
        "technical depth",
        "architecture understanding",
        "evidence from own work",
    ],
    QuestionCategory.CS_FUNDAMENTALS: [
        "conceptual accuracy",
        "clarity of explanation",
        "practical understanding",
        "relevance to stated experience",
    ],
    QuestionCategory.DSA: [
        "problem understanding",
        "approach and complexity",
        "correctness",
        "communication",
    ],
    QuestionCategory.BEHAVIORAL: [
        "clarity",
        "relevance",
        "communication",
        "specific examples",
    ],
}


class GeneratedQuestionValidator:
    @classmethod
    def validate(
        cls,
        question: GeneratedQuestion,
        *,
        context: QuestionGenerationContext | None = None,
    ) -> GeneratedQuestion:
        cls._ensure_limits(question)
        text = _MULTI_SPACE.sub(" ", question.text.strip())
        if context is not None:
            project_names = [
                sanitize_project_name(project.name) for project in context.resume.projects
            ]
            text = normalize_project_references_in_text(text, project_names)

        rubric = _normalize_list(question.evaluation_rubric)
        if not rubric:
            rubric = list(_DEFAULT_RUBRIC[question.category])

        return GeneratedQuestion(
            text=text,
            category=question.category,
            expected_topics=_normalize_list(question.expected_topics),
            difficulty=question.difficulty,
            evaluation_rubric=rubric,
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
