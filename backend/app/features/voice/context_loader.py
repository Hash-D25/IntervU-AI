"""Load interview-aware transcription context for a user."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.features.interview.planning.schemas import InterviewMetadata
from app.features.interview.repository import InterviewRepository
from app.features.voice.context_builder import (
    build_transcription_context,
    empty_transcription_context,
)
from app.features.voice.schemas import TranscriptionContext


class TranscriptionContextLoader:
    def __init__(self, interviews: InterviewRepository) -> None:
        self._interviews = interviews

    async def load(
        self,
        *,
        user_id: UUID,
        interview_id: UUID | None,
    ) -> TranscriptionContext:
        if interview_id is None:
            return empty_transcription_context()
        interview = await self._interviews.get_for_user(interview_id, user_id)
        if interview is None:
            raise NotFoundError("Interview not found")
        metadata = InterviewMetadata.model_validate(interview.interview_metadata)
        return build_transcription_context(metadata)


def create_transcription_context_loader(session: AsyncSession) -> TranscriptionContextLoader:
    return TranscriptionContextLoader(InterviewRepository(session))
