"""Feedback synthesis filter tests."""

from app.features.evaluation.schemas import (
    DimensionScore,
    EvaluationDimension,
)
from app.features.feedback.schemas import EvaluatedAnswerSummary, FeedbackContext, FeedbackResult
from app.features.feedback.synthesis_filter import refine_feedback


def _intro_transcript() -> str:
    return (
        "Hello, and thank you for the opportunity. My name is Harshita, and I'm currently "
        "pursuing a B.Tech in Computer Science and Engineering at NIT Srinagar. Outside of "
        "internships, I enjoy building projects. One of my recent projects is an AI-powered "
        "browser automation assistant. I also actively practice competitive programming and "
        "have solved over 800 problems across platforms like LeetCode and Codeforces. I'm "
        "interested in the SDE Intern role at EPAM because of the opportunity to work on "
        "real-world software solutions. At Tulifo I owned the auth module end-to-end — "
        "schema design in Prisma, JWT refresh flow, and API tests."
    )


def _harshita_context() -> FeedbackContext:
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
                answer_transcript=_intro_transcript(),
                overall_score=7.98,
                dimension_scores=[
                    DimensionScore(
                        dimension=EvaluationDimension.DEPTH,
                        score=4.0,
                        rationale="Light on technical depth.",
                    )
                ],
                answer_improvements=[
                    "Offer more detailed explanations of your technical achievements, "
                    "such as the specifics of implementing authentication at Tulifo AI.",
                    "Provide more context about how your competitive programming experience "
                    "has helped you develop strong analytical thinking.",
                    "Consider exploring how your projects align with EPAM's focus.",
                ],
            )
        ],
        overall_average_score=8.32,
        dimension_averages={
            "technical_accuracy": 8.75,
            "completeness": 8.5,
            "communication": 9.0,
            "depth": 6.75,
            "examples": 8.0,
        },
    )


def test_refine_feedback_removes_contradictory_and_verbatim_weaknesses() -> None:
    raw = FeedbackResult(
        summary="Good interview overall.",
        strengths=["Clear communication"],
        weaknesses=[
            "Offer more detailed explanations of your technical achievements, "
            "such as the specifics of implementing authentication at Tulifo AI.",
            "Provide more context about how your competitive programming experience "
            "has helped you develop strong analytical thinking.",
            "Consider exploring how your projects align with EPAM's focus.",
        ],
        recommendations=[
            "Study and prepare examples that demonstrate how your projects align with EPAM.",
            "Provide more context about competitive programming and DSA.",
        ],
        learning_roadmap=["Week 1: practice depth"],
        overall_score=8.32,
        generator_name="llm",
    )

    refined = refine_feedback(raw, _harshita_context())

    assert all(
        "authentication" not in item.casefold() or "tradeoff" in item.casefold()
        for item in refined.weaknesses
    )
    assert all("competitive programming" not in item.casefold() for item in refined.weaknesses)
    assert all("align with epam" not in item.casefold() for item in refined.recommendations)
    assert len(refined.weaknesses) >= 2
    assert len(refined.recommendations) >= 3
    assert any("depth" in item.casefold() for item in refined.weaknesses)
