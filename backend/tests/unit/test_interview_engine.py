"""Interview execution engine unit tests."""

import pytest

from app.features.interview.execution.engine import InterviewEngine
from app.features.interview.execution.exceptions import InvalidTransitionError
from app.features.interview.execution.schemas import (
    EngineStatus,
    InterviewPhase,
    SessionQuestion,
)
from app.features.interview.planning.schemas import InterviewType


def _question(phase: InterviewPhase, position: int, text: str) -> SessionQuestion:
    return SessionQuestion(
        position=position,
        phase=phase,
        text=text,
        category="project",
        difficulty="medium",
        expected_topics=["topic-a"],
        evaluation_rubric=["clarity"],
    )


def test_build_context_has_explicit_phase_sequence() -> None:
    engine = InterviewEngine()
    context = engine.build_context(
        interview_type=InterviewType.TECHNICAL,
        company_name="EPAM",
        target_role="SDE intern",
    )

    assert context.status == EngineStatus.NOT_STARTED
    assert context.phase is None
    assert context.phase_sequence == [
        InterviewPhase.INTRODUCTION,
        InterviewPhase.RESUME,
        InterviewPhase.PROJECTS,
        InterviewPhase.CS_FUNDAMENTALS,
        InterviewPhase.FINAL,
    ]
    assert context.questions == []
    assert context.awaiting_answer is False


def test_start_moves_to_introduction_phase() -> None:
    engine = InterviewEngine()
    context = engine.build_context(
        interview_type=InterviewType.TECHNICAL,
        company_name="EPAM",
        target_role="SDE intern",
    )

    started = engine.start(context)
    snapshot = engine.snapshot(started)

    assert started.status == EngineStatus.IN_PROGRESS
    assert started.phase == InterviewPhase.INTRODUCTION
    assert snapshot.allowed_transitions == [InterviewPhase.INTRODUCTION]


def test_attach_and_submit_answer_advances_through_phases() -> None:
    engine = InterviewEngine()
    context = engine.start(
        engine.build_context(
            interview_type=InterviewType.BEHAVIORAL,
            company_name="EPAM",
            target_role="SDE intern",
        )
    )

    context = engine.attach_question(
        context,
        _question(InterviewPhase.INTRODUCTION, 0, "Tell me about yourself."),
    )
    assert context.awaiting_answer is True
    assert engine.snapshot(context).current_question is not None
    assert engine.snapshot(context).previous_questions == []

    context = engine.submit_answer(context, "I am a backend engineer.")
    assert context.awaiting_answer is False
    assert context.phase == InterviewPhase.INTRODUCTION
    context = engine.advance_after_answer(context)
    assert context.phase == InterviewPhase.RESUME
    assert len(engine.snapshot(context).previous_questions) == 1

    context = engine.attach_question(
        context,
        _question(InterviewPhase.RESUME, 1, "Walk me through your resume."),
    )
    context = engine.submit_answer(context, "I built APIs with FastAPI.")
    context = engine.advance_after_answer(context)
    assert context.phase == InterviewPhase.BEHAVIORAL

    context = engine.attach_question(
        context,
        _question(InterviewPhase.BEHAVIORAL, 2, "Tell me about teamwork."),
    )
    context = engine.submit_answer(context, "I collaborated on a team project.")
    context = engine.advance_after_answer(context)
    assert context.status == EngineStatus.COMPLETED
    assert context.phase == InterviewPhase.FINAL
    assert engine.snapshot(context).current_question is None
    assert len(engine.snapshot(context).previous_questions) == 3


def test_cannot_submit_answer_without_current_question() -> None:
    engine = InterviewEngine()
    context = engine.start(
        engine.build_context(
            interview_type=InterviewType.TECHNICAL,
            company_name="EPAM",
            target_role="SDE intern",
        )
    )

    with pytest.raises(InvalidTransitionError):
        engine.submit_answer(context, "No question yet.")


def test_cannot_attach_question_while_awaiting_answer() -> None:
    engine = InterviewEngine()
    context = engine.attach_question(
        engine.start(
            engine.build_context(
                interview_type=InterviewType.TECHNICAL,
                company_name="EPAM",
                target_role="SDE intern",
            )
        ),
        _question(InterviewPhase.INTRODUCTION, 0, "Intro question"),
    )

    with pytest.raises(InvalidTransitionError):
        engine.attach_question(
            context,
            _question(InterviewPhase.INTRODUCTION, 1, "Another intro question"),
        )
