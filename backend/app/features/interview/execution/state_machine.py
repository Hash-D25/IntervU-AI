"""Explicit phase transitions for the interview execution engine."""

from app.features.interview.execution.schemas import (
    EngineStatus,
    InterviewPhase,
    SessionContext,
)
from app.features.interview.planning.schemas import InterviewType

_DEFAULT_QUESTIONS_PER_PHASE: dict[InterviewPhase, int] = {
    InterviewPhase.INTRODUCTION: 1,
    InterviewPhase.RESUME: 1,
    InterviewPhase.PROJECTS: 1,
    InterviewPhase.CS_FUNDAMENTALS: 1,
    InterviewPhase.BEHAVIORAL: 1,
    InterviewPhase.FINAL: 0,
}

_PHASE_SEQUENCES: dict[InterviewType, list[InterviewPhase]] = {
    InterviewType.TECHNICAL: [
        InterviewPhase.INTRODUCTION,
        InterviewPhase.RESUME,
        InterviewPhase.PROJECTS,
        InterviewPhase.CS_FUNDAMENTALS,
        InterviewPhase.FINAL,
    ],
    InterviewType.BEHAVIORAL: [
        InterviewPhase.INTRODUCTION,
        InterviewPhase.RESUME,
        InterviewPhase.BEHAVIORAL,
        InterviewPhase.FINAL,
    ],
    InterviewType.MIXED: [
        InterviewPhase.INTRODUCTION,
        InterviewPhase.RESUME,
        InterviewPhase.PROJECTS,
        InterviewPhase.CS_FUNDAMENTALS,
        InterviewPhase.BEHAVIORAL,
        InterviewPhase.FINAL,
    ],
}


def phase_sequence_for(interview_type: InterviewType) -> list[InterviewPhase]:
    return list(_PHASE_SEQUENCES[interview_type])


def default_questions_per_phase() -> dict[InterviewPhase, int]:
    return dict(_DEFAULT_QUESTIONS_PER_PHASE)


def questions_asked_in_phase(context: SessionContext, phase: InterviewPhase) -> int:
    return sum(1 for question in context.questions if question.phase == phase)


def questions_remaining_in_phase(context: SessionContext) -> int:
    if context.phase is None:
        return 0
    quota = context.questions_per_phase.get(context.phase, 0)
    return max(quota - questions_asked_in_phase(context, context.phase), 0)


def next_phase(context: SessionContext) -> InterviewPhase | None:
    if context.phase is None:
        return None
    sequence = context.phase_sequence
    try:
        index = sequence.index(context.phase)
    except ValueError:
        return None
    if index + 1 >= len(sequence):
        return None
    return sequence[index + 1]


def allowed_phase_transitions(context: SessionContext) -> list[InterviewPhase]:
    if context.status == EngineStatus.NOT_STARTED:
        if context.phase_sequence:
            return [context.phase_sequence[0]]
        return []
    if context.status == EngineStatus.COMPLETED:
        return []
    if context.awaiting_answer or context.phase is None:
        return []
    if context.phase == InterviewPhase.FINAL:
        return []
    if questions_remaining_in_phase(context) > 0:
        return [context.phase]
    upcoming = next_phase(context)
    if upcoming is None:
        return [InterviewPhase.FINAL]
    return [upcoming]
