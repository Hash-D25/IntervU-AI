"""Generated question validator tests."""

from app.features.interview.planning.schemas import InterviewPlan, InterviewType
from app.features.interview.question_generation.schemas import (
    Difficulty,
    GeneratedQuestion,
    QuestionCategory,
    QuestionGenerationContext,
)
from app.features.interview.question_generation.validator import GeneratedQuestionValidator
from app.features.resume.parsing.schemas import ParsedResume, ProjectEntry


def _sample_context() -> QuestionGenerationContext:
    return QuestionGenerationContext(
        company_name="EPAM",
        target_role="SDE intern",
        interview_type=InterviewType.TECHNICAL,
        interview_plan=InterviewPlan(
            focus_areas=["Python"],
            question_mix=["project_walkthrough"],
            estimated_rounds=2,
            follow_up_strategy="Ask follow-ups.",
            evaluation_axes=["clarity"],
        ),
        resume=ParsedResume(
            skills=["Python", "FastAPI", "PostgreSQL"],
            projects=[
                ProjectEntry(name="UncDoIt - AI Web Navigation Assistant"),
                ProjectEntry(name="ytNotes : YouTube Notes Chrome Extension"),
            ],
            technologies=["FastAPI", "PostgreSQL"],
        ),
    )


def test_validator_fills_empty_rubric() -> None:
    question = GeneratedQuestion(
        text="Explain your project architecture?",
        category=QuestionCategory.PROJECT,
        expected_topics=["architecture"],
        difficulty=Difficulty.EASY,
        evaluation_rubric=[],
    )

    validated = GeneratedQuestionValidator.validate(question, context=_sample_context())

    assert validated.evaluation_rubric
    assert "technical depth" in validated.evaluation_rubric


def test_validator_aligns_project_names_in_question_text() -> None:
    question = GeneratedQuestion(
        text=(
            "Compare UncDoIt - AI Web Navigation Assistant Link with "
            "ytNotes : YouTube Notes Chrome Extension."
        ),
        category=QuestionCategory.PROJECT,
        expected_topics=["architecture"],
        difficulty=Difficulty.EASY,
        evaluation_rubric=["clarity"],
    )

    validated = GeneratedQuestionValidator.validate(question, context=_sample_context())

    assert "Assistant Link" not in validated.text
    assert "UncDoIt - AI Web Navigation Assistant" in validated.text
