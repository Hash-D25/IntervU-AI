"""Post-evaluation validation and normalization."""

import re

from app.core.exceptions import ParseError
from app.features.evaluation.improvement_filter import filter_contradictory_improvements
from app.features.evaluation.phase_guidance import phase_dimension_weights
from app.features.evaluation.schemas import (
    REQUIRED_DIMENSIONS,
    AnswerEvaluationResult,
    DimensionScore,
    EvaluationContext,
    EvaluationDimension,
)

_MAX_ITEMS = 6
_MULTI_SPACE = re.compile(r"\s+")

_DIMENSION_ALIASES: dict[str, EvaluationDimension] = {
    "technical_accuracy": EvaluationDimension.TECHNICAL_ACCURACY,
    "technical accuracy": EvaluationDimension.TECHNICAL_ACCURACY,
    "accuracy": EvaluationDimension.TECHNICAL_ACCURACY,
    "completeness": EvaluationDimension.COMPLETENESS,
    "complete": EvaluationDimension.COMPLETENESS,
    "communication": EvaluationDimension.COMMUNICATION,
    "clarity": EvaluationDimension.COMMUNICATION,
    "depth": EvaluationDimension.DEPTH,
    "depth of understanding": EvaluationDimension.DEPTH,
    "examples": EvaluationDimension.EXAMPLES,
    "example": EvaluationDimension.EXAMPLES,
    "evidence": EvaluationDimension.EXAMPLES,
}


class AnswerEvaluationValidator:
    @classmethod
    def validate(
        cls,
        evaluation: AnswerEvaluationResult,
        *,
        context: EvaluationContext | None = None,
    ) -> AnswerEvaluationResult:
        cls._ensure_limits(evaluation)
        scores = cls._normalize_scores(evaluation.scores)
        strengths = _normalize_list(evaluation.strengths)
        improvements = _normalize_list(evaluation.improvements)
        if context is not None:
            improvements = filter_contradictory_improvements(
                improvements,
                context.answer_transcript,
            )
        overall = cls._weighted_overall(scores, context)
        return AnswerEvaluationResult(
            scores=scores,
            overall_score=overall,
            strengths=strengths,
            improvements=improvements,
            evaluator_name=evaluation.evaluator_name.strip(),
        )

    @classmethod
    def _weighted_overall(
        cls,
        scores: list[DimensionScore],
        context: EvaluationContext | None,
    ) -> float:
        weights = phase_dimension_weights(context.phase) if context else {}
        total_weight = 0.0
        weighted_sum = 0.0
        for score in scores:
            weight = weights.get(score.dimension, 1.0)
            weighted_sum += score.score * weight
            total_weight += weight
        if total_weight <= 0:
            return round(sum(s.score for s in scores) / len(scores), 2)
        return round(weighted_sum / total_weight, 2)

    @classmethod
    def _normalize_scores(cls, scores: list[DimensionScore]) -> list[DimensionScore]:
        by_dimension: dict[EvaluationDimension, DimensionScore] = {}
        for score in scores:
            dimension = _resolve_dimension(score.dimension)
            rationale = _MULTI_SPACE.sub(" ", score.rationale.strip())
            if not rationale:
                raise ParseError("Evaluation rationale cannot be empty")
            clamped = max(0.0, min(10.0, float(score.score)))
            by_dimension[dimension] = DimensionScore(
                dimension=dimension,
                score=round(clamped, 2),
                rationale=rationale,
            )

        missing = [dim for dim in REQUIRED_DIMENSIONS if dim not in by_dimension]
        if missing:
            raise ParseError(f"Evaluation missing required dimensions: {', '.join(missing)}")

        return [by_dimension[dimension] for dimension in REQUIRED_DIMENSIONS]

    @classmethod
    def _ensure_limits(cls, evaluation: AnswerEvaluationResult) -> None:
        if len(evaluation.strengths) > _MAX_ITEMS or len(evaluation.improvements) > _MAX_ITEMS:
            raise ParseError("Evaluation has too many strengths or improvements")


def _resolve_dimension(value: EvaluationDimension | str) -> EvaluationDimension:
    if isinstance(value, EvaluationDimension):
        return value
    key = value.strip().casefold()
    if key in _DIMENSION_ALIASES:
        return _DIMENSION_ALIASES[key]
    try:
        return EvaluationDimension(key)
    except ValueError as exc:
        raise ParseError(f"Unknown evaluation dimension: {value}") from exc


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
