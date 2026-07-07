"""Feedback context builder unit tests."""

from app.features.evaluation.schemas import (
    AnswerEvaluationResult,
    DimensionScore,
    EvaluationDimension,
)
from app.features.feedback.context_builder import build_feedback_context
from app.features.interview.execution.schemas import (
    EngineStatus,
    InterviewPhase,
    SessionContext,
    SessionQuestion,
)
from app.features.interview.models import Interview, InterviewStatus
from app.features.interview.planning.schemas import InterviewType


def _evaluation(score: float = 8.0) -> AnswerEvaluationResult:
    return AnswerEvaluationResult(
        scores=[
            DimensionScore(
                dimension=dim,
                score=score,
                rationale="Solid answer.",
            )
            for dim in EvaluationDimension
        ],
        overall_score=score,
        strengths=["Clear communication"],
        improvements=["Add more metrics"],
        evaluator_name="llm",
    )


def test_build_feedback_context_aggregates_evaluated_answers() -> None:
    session = SessionContext(
        status=EngineStatus.COMPLETED,
        phase=InterviewPhase.FINAL,
        interview_type=InterviewType.TECHNICAL,
        company_name="EPAM",
        target_role="SDE intern",
        questions=[
            SessionQuestion(
                position=0,
                phase=InterviewPhase.INTRODUCTION,
                text="Tell me about yourself.",
                category="behavioral",
                difficulty="easy",
                answered=True,
                answer_transcript="I am a backend engineer with FastAPI experience.",
                evaluation=_evaluation(8.0),
            ),
            SessionQuestion(
                position=1,
                phase=InterviewPhase.RESUME,
                text="Walk me through your resume.",
                category="project",
                difficulty="medium",
                answered=True,
                answer_transcript="I built UncDoIt and ytNotes.",
                evaluation=_evaluation(7.5),
            ),
        ],
    )
    interview = Interview(
        user_id="00000000-0000-0000-0000-000000000001",
        role="SDE intern",
        company="EPAM",
        interview_type=InterviewType.TECHNICAL,
        status=InterviewStatus.COMPLETED,
        interview_metadata={
            "company_name": "EPAM",
            "target_role": "SDE intern",
            "interview_type": "technical",
            "has_job_description": False,
            "resume_summary": {
                "skills": ["Python"],
                "technologies": ["FastAPI"],
                "project_names": ["UncDoIt"],
                "experience_titles": ["Intern"],
            },
            "context_sources": ["parsed_resume"],
        },
        interview_plan={
            "focus_areas": ["Python"],
            "question_mix": ["technical_core"],
            "estimated_rounds": 2,
            "follow_up_strategy": "Ask follow-ups.",
            "evaluation_axes": ["clarity"],
        },
        execution_context=session.model_dump(mode="json"),
    )

    context = build_feedback_context(interview)

    assert len(context.evaluated_answers) == 2
    assert context.overall_average_score == 7.75
    assert context.dimension_averages["communication"] == 7.75
    assert context.recurring_strengths == ["Clear communication"]
