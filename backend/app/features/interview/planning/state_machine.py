"""State machine rules for interview session flow."""

from app.features.interview.planning.schemas import SessionState, SessionStateSnapshot

_ALLOWED_TRANSITIONS: dict[SessionState, list[SessionState]] = {
    SessionState.DRAFT: [SessionState.READY],
    SessionState.READY: [SessionState.ASKING_INTRO, SessionState.FINISHED],
    SessionState.ASKING_INTRO: [SessionState.AWAITING_ANSWER, SessionState.ASKING_CORE],
    SessionState.ASKING_CORE: [SessionState.AWAITING_ANSWER, SessionState.ASKING_FOLLOW_UP],
    SessionState.ASKING_FOLLOW_UP: [SessionState.AWAITING_ANSWER, SessionState.FINISHED],
    SessionState.AWAITING_ANSWER: [SessionState.EVALUATING_ANSWER],
    SessionState.EVALUATING_ANSWER: [
        SessionState.ASKING_CORE,
        SessionState.ASKING_FOLLOW_UP,
        SessionState.FINISHED,
    ],
    SessionState.FINISHED: [],
}


def build_state_snapshot(state: SessionState) -> SessionStateSnapshot:
    return SessionStateSnapshot(
        current=state,
        allowed_transitions=_ALLOWED_TRANSITIONS[state],
        question_index=0,
        answered_questions=0,
    )
