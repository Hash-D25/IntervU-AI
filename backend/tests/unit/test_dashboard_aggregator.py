"""Dashboard aggregator unit tests."""

from datetime import UTC, datetime
from uuid import uuid4

from app.features.dashboard.aggregator import build_dashboard_summary
from app.features.evaluation.schemas import (
    AnswerEvaluationResult,
    DimensionScore,
    EvaluationDimension,
)
from app.features.feedback.models import FeedbackReport
from app.features.interview.execution.schemas import (
    EngineStatus,
    InterviewPhase,
    SessionContext,
    SessionQuestion,
)
from app.features.interview.models import Interview, InterviewStatus
from app.features.interview.planning.schemas import InterviewType


def _evaluation(score: float) -> AnswerEvaluationResult:
    return AnswerEvaluationResult(
        scores=[
            DimensionScore(dimension=dim, score=score, rationale="ok")
            for dim in EvaluationDimension
        ],
        overall_score=score,
        strengths=["Clear communication"],
        improvements=["Add tradeoffs"],
        evaluator_name="fake",
    )


def _interview(
    *,
    company: str,
    role: str,
    status: InterviewStatus,
    score: float,
    with_feedback: bool = False,
) -> Interview:
    interview_id = uuid4()
    engine_status = (
        EngineStatus.COMPLETED
        if status == InterviewStatus.COMPLETED
        else EngineStatus.IN_PROGRESS
    )
    session = SessionContext(
        status=engine_status,
        phase=InterviewPhase.PROJECTS,
        interview_type=InterviewType.TECHNICAL,
        company_name=company,
        target_role=role,
        questions=[
            SessionQuestion(
                id=uuid4(),
                position=0,
                phase=InterviewPhase.PROJECTS,
                text="Tell me about JWT auth.",
                category="project",
                difficulty="medium",
                answered=True,
                answer_transcript="We use JWT tokens.",
                evaluation=_evaluation(score),
            )
        ],
    )
    interview = Interview(
        id=interview_id,
        user_id=uuid4(),
        role=role,
        company=company,
        interview_type=InterviewType.TECHNICAL,
        status=status,
        interview_metadata={
            "company_name": company,
            "target_role": role,
            "interview_type": "technical",
        },
        interview_plan={
            "focus_areas": ["backend"],
            "question_mix": ["project"],
            "estimated_rounds": 2,
            "follow_up_strategy": "Probe claims.",
            "evaluation_axes": ["depth"],
        },
        execution_context=session.model_dump(mode="json"),
        created_at=datetime(2026, 1, 10, tzinfo=UTC),
        updated_at=datetime(2026, 1, 10, tzinfo=UTC),
    )
    if with_feedback:
        interview.feedback_report = FeedbackReport(
            interview_id=interview_id,
            summary="Solid session.",
            strengths=["Clear communication"],
            weaknesses=["Needs deeper tradeoffs"],
            suggestions=["Practice system design"],
            roadmap=["Review caching patterns"],
            overall_score=score,
        )
    return interview


def test_build_dashboard_summary_aggregates_history_and_scores() -> None:
    interviews = [
        _interview(company="EPAM", role="SDE", status=InterviewStatus.COMPLETED, score=7.5),
        _interview(
            company="Google",
            role="Intern",
            status=InterviewStatus.IN_PROGRESS,
            score=8.0,
            with_feedback=True,
        ),
    ]

    summary = build_dashboard_summary(interviews)

    assert summary.total_interviews == 2
    assert summary.completed_interviews == 1
    assert len(summary.interview_history) == 2
    assert summary.interview_history[0].company_name == "EPAM"
    assert summary.category_scores[0].category == "project"
    assert summary.category_scores[0].average_score == 7.75
    assert "Clear communication" in summary.strengths
    assert "Needs deeper tradeoffs" in summary.weaknesses
    assert len(summary.progress_over_time) == 2
    assert "technical_accuracy" in summary.dimension_averages
