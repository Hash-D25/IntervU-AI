"""Map execution snapshots to API DTOs."""

from app.features.interview.execution.schemas import EngineSnapshot
from app.features.interview.schemas import ExecutionSnapshotResponse


def to_execution_snapshot_response(snapshot: EngineSnapshot) -> ExecutionSnapshotResponse:
    return ExecutionSnapshotResponse(
        status=snapshot.status,
        phase=snapshot.phase,
        current_question=snapshot.current_question,
        previous_questions=snapshot.previous_questions,
        allowed_transitions=snapshot.allowed_transitions,
        session_context=snapshot.session_context,
    )
