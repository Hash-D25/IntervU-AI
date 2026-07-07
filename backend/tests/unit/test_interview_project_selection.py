"""Interview project selection for phase-diverse questions."""

from app.features.interview.execution.project_selection import (
    build_execution_hints,
    projects_covered_in_questions,
)
from app.features.interview.execution.schemas import (
    EngineStatus,
    InterviewPhase,
    SessionContext,
    SessionQuestion,
)
from app.features.interview.planning.schemas import InterviewType


def _session(
    *,
    phase: InterviewPhase,
    questions: list[SessionQuestion] | None = None,
) -> SessionContext:
    return SessionContext(
        status=EngineStatus.IN_PROGRESS,
        phase=phase,
        interview_type=InterviewType.TECHNICAL,
        company_name="EPAM",
        target_role="SDE intern",
        phase_sequence=[
            InterviewPhase.INTRODUCTION,
            InterviewPhase.RESUME,
            InterviewPhase.PROJECTS,
            InterviewPhase.CS_FUNDAMENTALS,
            InterviewPhase.FINAL,
        ],
        questions=questions or [],
    )


def test_resume_phase_prefers_comparing_first_two_projects() -> None:
    hints = build_execution_hints(
        session=_session(phase=InterviewPhase.RESUME),
        project_names=[
            "UncDoIt - AI Web Navigation Assistant",
            "ytNotes : YouTube Notes Chrome Extension",
            "GitHub Repository Browser : Private Repo Viewer",
        ],
        experience_titles=["SDE Intern"],
    )

    assert hints["execution_phase"] == InterviewPhase.RESUME
    assert hints["comparison_project_names"] == [
        "UncDoIt - AI Web Navigation Assistant",
        "ytNotes : YouTube Notes Chrome Extension",
    ]
    assert "comparing" in str(hints["phase_instruction"]).lower()


def test_projects_phase_picks_unused_project() -> None:
    previous = [
        SessionQuestion(
            position=1,
            phase=InterviewPhase.RESUME,
            text="Compare UncDoIt - AI Web Navigation Assistant and ytNotes.",
            category="project",
            difficulty="medium",
            answered=True,
            answer_transcript="answer",
        )
    ]
    hints = build_execution_hints(
        session=_session(phase=InterviewPhase.PROJECTS, questions=previous),
        project_names=[
            "UncDoIt - AI Web Navigation Assistant",
            "ytNotes : YouTube Notes Chrome Extension",
            "GitHub Repository Browser : Private Repo Viewer",
        ],
        experience_titles=["SDE Intern"],
    )

    assert hints["focus_project_names"] == ["GitHub Repository Browser : Private Repo Viewer"]
    assert "GitHub Repository Browser" in str(hints["phase_instruction"])
    assert "Deep-dive ONLY" in str(hints["phase_instruction"])


def test_projects_covered_detects_mentioned_projects() -> None:
    questions = [
        SessionQuestion(
            position=1,
            phase=InterviewPhase.RESUME,
            text="Walk me through UncDoIt - AI Web Navigation Assistant architecture.",
            category="project",
            difficulty="medium",
        )
    ]
    names = [
        "UncDoIt - AI Web Navigation Assistant",
        "ytNotes : YouTube Notes Chrome Extension",
    ]

    covered = projects_covered_in_questions(questions, names)

    assert covered == ["UncDoIt - AI Web Navigation Assistant"]
