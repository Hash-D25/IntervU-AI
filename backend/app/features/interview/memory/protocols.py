"""Interview memory contracts for swappable persistence strategies."""

from typing import Protocol, runtime_checkable
from uuid import UUID

from app.features.interview.execution.schemas import SessionContext
from app.features.interview.memory.schemas import InterviewMemory


@runtime_checkable
class InterviewMemoryBuilder(Protocol):
    """Rebuild compact memory from the live session."""

    name: str

    def rebuild(self, session: SessionContext) -> InterviewMemory: ...


@runtime_checkable
class InterviewMemoryStore(Protocol):
    """Future persistence (DB / vector). Not required for v1 session memory."""

    name: str

    async def load(self, interview_id: UUID) -> InterviewMemory: ...

    async def save(self, interview_id: UUID, memory: InterviewMemory) -> None: ...
