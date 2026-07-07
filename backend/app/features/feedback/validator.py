"""Post-generation validation and normalization for feedback."""

import re

from app.core.exceptions import ParseError
from app.features.feedback.schemas import FeedbackContext, FeedbackResult
from app.features.feedback.synthesis_filter import refine_feedback

_MAX_ITEMS = 8
_MULTI_SPACE = re.compile(r"\s+")


class FeedbackValidator:
    @classmethod
    def validate(
        cls,
        feedback: FeedbackResult,
        *,
        context: FeedbackContext | None = None,
    ) -> FeedbackResult:
        cls._ensure_limits(feedback)
        overall = feedback.overall_score
        if context is not None:
            overall = context.overall_average_score
            feedback = refine_feedback(feedback, context)
        return FeedbackResult(
            summary=_MULTI_SPACE.sub(" ", feedback.summary.strip()),
            strengths=_normalize_list(feedback.strengths),
            weaknesses=_normalize_list(feedback.weaknesses),
            recommendations=_normalize_list(feedback.recommendations),
            learning_roadmap=_normalize_list(feedback.learning_roadmap),
            overall_score=round(max(0.0, min(10.0, float(overall))), 2),
            generator_name=feedback.generator_name.strip(),
        )

    @classmethod
    def _ensure_limits(cls, feedback: FeedbackResult) -> None:
        if not feedback.summary.strip():
            raise ParseError("Feedback summary cannot be empty")
        for field_name, values in (
            ("strengths", feedback.strengths),
            ("weaknesses", feedback.weaknesses),
            ("recommendations", feedback.recommendations),
            ("learning_roadmap", feedback.learning_roadmap),
        ):
            if not values:
                raise ParseError(f"Feedback {field_name} cannot be empty")
            if len(values) > _MAX_ITEMS:
                raise ParseError(f"Feedback {field_name} has too many items")


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
        if len(normalized) >= _MAX_ITEMS:
            break
    return normalized
