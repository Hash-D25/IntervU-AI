"""Answer evaluation validator unit tests."""

import pytest

from app.core.exceptions import ParseError
from app.features.evaluation.schemas import (
    REQUIRED_DIMENSIONS,
    AnswerEvaluationResult,
    DimensionScore,
    EvaluationContext,
    EvaluationDimension,
)
from app.features.evaluation.validator import AnswerEvaluationValidator


def _sample_scores() -> list[DimensionScore]:
    return [
        DimensionScore(dimension=dim, score=7.0, rationale="Solid evidence in the answer.")
        for dim in REQUIRED_DIMENSIONS
    ]


def test_validator_computes_overall_score() -> None:
    result = AnswerEvaluationValidator.validate(
        AnswerEvaluationResult(
            scores=_sample_scores(),
            overall_score=0.0,
            strengths=["Clear structure"],
            improvements=["Add metrics"],
            evaluator_name="llm",
        )
    )

    assert result.overall_score == 7.0
    assert len(result.scores) == 5
    assert result.scores[0].dimension == EvaluationDimension.TECHNICAL_ACCURACY


def test_validator_requires_all_dimensions() -> None:
    with pytest.raises(ParseError):
        AnswerEvaluationValidator.validate(
            AnswerEvaluationResult(
                scores=[
                    DimensionScore(
                        dimension=EvaluationDimension.TECHNICAL_ACCURACY,
                        score=8.0,
                        rationale="Accurate.",
                    )
                ],
                overall_score=8.0,
                evaluator_name="llm",
            )
        )


def test_validator_filters_contradictory_improvements() -> None:
    context = EvaluationContext(
        question_text="Tell me about yourself.",
        answer_transcript=(
            "I solved 800+ problems on LeetCode and Codeforces and built UncDoIt."
        ),
        category="behavioral",
        phase="introduction",
        difficulty="easy",
        company_name="EPAM",
        target_role="SDE intern",
    )
    result = AnswerEvaluationValidator.validate(
        AnswerEvaluationResult(
            scores=_sample_scores(),
            overall_score=0.0,
            strengths=["Clear intro"],
            improvements=[
                "Quantify the number of problems solved on LeetCode.",
                "Describe a specific technical challenge you solved.",
            ],
            evaluator_name="llm",
        ),
        context=context,
    )

    assert len(result.improvements) == 1
    assert "technical challenge" in result.improvements[0].lower()


def test_validator_uses_phase_weighted_overall_for_introduction() -> None:
    context = EvaluationContext(
        question_text="Tell me about yourself.",
        answer_transcript="Structured intro with examples.",
        category="behavioral",
        phase="introduction",
        difficulty="easy",
        company_name="EPAM",
        target_role="SDE intern",
    )
    scores = [
        DimensionScore(
            dimension=EvaluationDimension.TECHNICAL_ACCURACY,
            score=7.0,
            rationale="Plausible claims.",
        ),
        DimensionScore(
            dimension=EvaluationDimension.COMPLETENESS,
            score=9.0,
            rationale="Covers background and motivation.",
        ),
        DimensionScore(
            dimension=EvaluationDimension.COMMUNICATION,
            score=9.0,
            rationale="Clear and structured.",
        ),
        DimensionScore(
            dimension=EvaluationDimension.DEPTH,
            score=7.0,
            rationale="Appropriate for intro.",
        ),
        DimensionScore(
            dimension=EvaluationDimension.EXAMPLES,
            score=9.0,
            rationale="Named projects and internship.",
        ),
    ]
    result = AnswerEvaluationValidator.validate(
        AnswerEvaluationResult(
            scores=scores,
            overall_score=0.0,
            strengths=["Strong intro"],
            improvements=[],
            evaluator_name="llm",
        ),
        context=context,
    )

    assert result.overall_score > 8.0
