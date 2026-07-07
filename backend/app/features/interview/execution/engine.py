"""Pure, deterministic interview execution engine."""

from datetime import UTC, datetime

from app.features.interview.execution.exceptions import InvalidTransitionError
from app.features.interview.execution.schemas import (
    EngineSnapshot,
    EngineStatus,
    InterviewPhase,
    SessionContext,
    SessionQuestion,
)
from app.features.interview.execution.state_machine import (
    allowed_phase_transitions,
    default_questions_per_phase,
    next_phase,
    phase_sequence_for,
    questions_remaining_in_phase,
)
from app.features.interview.planning.schemas import InterviewType


class InterviewEngine:
    """State transitions only — no I/O, no hidden mutable state."""

    @staticmethod
    def build_context(
        *,
        interview_type: InterviewType,
        company_name: str,
        target_role: str,
    ) -> SessionContext:
        sequence = phase_sequence_for(interview_type)
        return SessionContext(
            status=EngineStatus.NOT_STARTED,
            phase=None,
            interview_type=interview_type,
            company_name=company_name.strip(),
            target_role=target_role.strip(),
            phase_sequence=sequence,
            questions_per_phase=default_questions_per_phase(),
            questions=[],
            awaiting_answer=False,
        )

    @staticmethod
    def start(context: SessionContext) -> SessionContext:
        if context.status != EngineStatus.NOT_STARTED:
            raise InvalidTransitionError("Interview execution has already started")
        if not context.phase_sequence:
            raise InvalidTransitionError("Interview has no configured phases")
        first_phase = context.phase_sequence[0]
        return context.model_copy(
            update={
                "status": EngineStatus.IN_PROGRESS,
                "phase": first_phase,
                "awaiting_answer": False,
                "started_at": datetime.now(UTC),
            }
        )

    @staticmethod
    def attach_question(context: SessionContext, question: SessionQuestion) -> SessionContext:
        if context.status != EngineStatus.IN_PROGRESS:
            raise InvalidTransitionError("Interview is not in progress")
        if context.phase is None:
            raise InvalidTransitionError("Interview phase is not set")
        if context.awaiting_answer:
            raise InvalidTransitionError("Current question must be answered first")
        if question.phase != context.phase:
            raise InvalidTransitionError("Question phase does not match current phase")
        if context.phase == InterviewPhase.FINAL:
            raise InvalidTransitionError("No questions are asked in the final phase")

        questions = [*context.questions, question]
        return context.model_copy(
            update={
                "questions": questions,
                "awaiting_answer": True,
            }
        )

    @staticmethod
    def submit_answer(context: SessionContext, transcript: str) -> SessionContext:
        if context.status != EngineStatus.IN_PROGRESS:
            raise InvalidTransitionError("Interview is not in progress")
        if not context.awaiting_answer:
            raise InvalidTransitionError("No question is awaiting an answer")
        if not context.questions:
            raise InvalidTransitionError("No current question to answer")

        cleaned = transcript.strip()
        if not cleaned:
            raise InvalidTransitionError("Answer transcript cannot be empty")

        current = context.questions[-1]
        if current.answered:
            raise InvalidTransitionError("Current question has already been answered")

        answered_question = current.model_copy(
            update={
                "answered": True,
                "answer_transcript": cleaned,
            }
        )
        questions = [*context.questions[:-1], answered_question]
        updated = context.model_copy(
            update={
                "questions": questions,
                "awaiting_answer": False,
            }
        )
        return InterviewEngine._advance_after_answer(updated)

    @staticmethod
    def _advance_after_answer(context: SessionContext) -> SessionContext:
        if context.phase is None:
            return context
        if questions_remaining_in_phase(context) > 0:
            return context

        upcoming = next_phase(context)
        if upcoming is None or upcoming == InterviewPhase.FINAL:
            return context.model_copy(
                update={
                    "phase": InterviewPhase.FINAL,
                    "status": EngineStatus.COMPLETED,
                    "completed_at": datetime.now(UTC),
                }
            )
        return context.model_copy(update={"phase": upcoming})

    @staticmethod
    def snapshot(context: SessionContext) -> EngineSnapshot:
        current_question = None
        previous_questions: list[SessionQuestion] = []
        for question in context.questions:
            if question.answered:
                previous_questions.append(question)
            elif context.awaiting_answer:
                current_question = question

        return EngineSnapshot(
            status=context.status,
            phase=context.phase,
            current_question=current_question,
            previous_questions=previous_questions,
            allowed_transitions=allowed_phase_transitions(context),
            session_context=context,
        )
