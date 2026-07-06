"""FeedbackReport persistence."""

from uuid import UUID

from sqlalchemy import select

from app.db.repository import BaseRepository
from app.features.feedback.models import FeedbackReport


class FeedbackReportRepository(BaseRepository[FeedbackReport]):
    model = FeedbackReport

    async def get_for_interview(self, interview_id: UUID) -> FeedbackReport | None:
        result = await self.session.execute(
            select(FeedbackReport).where(FeedbackReport.interview_id == interview_id)
        )
        return result.scalar_one_or_none()
