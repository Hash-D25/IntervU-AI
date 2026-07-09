"""Dashboard orchestration."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.features.dashboard.aggregator import build_dashboard_summary
from app.features.dashboard.schemas import DashboardSummary
from app.features.interview.repository import InterviewRepository


class DashboardService:
    def __init__(self, session: AsyncSession, interviews: InterviewRepository) -> None:
        self._session = session
        self._interviews = interviews

    async def get_summary(self, user_id: UUID) -> DashboardSummary:
        items = await self._interviews.list_for_user_with_feedback(user_id)
        return build_dashboard_summary(items)
