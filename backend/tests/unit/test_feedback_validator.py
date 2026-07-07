"""Feedback validator unit tests."""

import pytest

from app.core.exceptions import ParseError
from app.features.feedback.schemas import FeedbackContext, FeedbackResult
from app.features.feedback.validator import FeedbackValidator


def _sample_context() -> FeedbackContext:
    from app.features.feedback.schemas import EvaluatedAnswerSummary

    return FeedbackContext(
        company_name="EPAM",
        target_role="SDE intern",
        interview_type="technical",
        evaluated_answers=[
            EvaluatedAnswerSummary(
                position=0,
                phase="introduction",
                category="behavioral",
                question_text="Tell me about yourself.",
                answer_transcript="Structured intro.",
                overall_score=8.0,
            )
        ],
        overall_average_score=8.0,
    )


def test_validator_normalizes_feedback_result() -> None:
    result = FeedbackValidator.validate(
        FeedbackResult(
            summary="Strong interview with clear communication.",
            strengths=["Clear communication", "Good project examples"],
            weaknesses=["Needs deeper system design detail"],
            recommendations=["Practice architecture tradeoff questions"],
            learning_roadmap=["Week 1: revise OOP fundamentals"],
            overall_score=0.0,
            generator_name="llm",
        ),
        context=_sample_context(),
    )

    assert result.overall_score == 8.0
    assert len(result.recommendations) >= 1


def test_validator_requires_non_empty_sections() -> None:
    with pytest.raises(ParseError):
        FeedbackValidator.validate(
            FeedbackResult(
                summary="Summary only.",
                strengths=[],
                weaknesses=["Needs work"],
                recommendations=["Practice more"],
                learning_roadmap=["Study DSA"],
                overall_score=7.0,
                generator_name="llm",
            )
        )
