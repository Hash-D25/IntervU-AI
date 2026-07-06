"""Resume metadata persistence."""

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select

from app.db.repository import BaseRepository
from app.features.resume.models import Resume


class ResumeRepository(BaseRepository[Resume]):
    model = Resume

    async def list_for_user(self, user_id: UUID) -> Sequence[Resume]:
        result = await self.session.execute(
            select(Resume).where(Resume.user_id == user_id).order_by(Resume.created_at.desc())
        )
        return result.scalars().all()

    async def get_for_user(self, resume_id: UUID, user_id: UUID) -> Resume | None:
        result = await self.session.execute(
            select(Resume).where(Resume.id == resume_id, Resume.user_id == user_id)
        )
        return result.scalar_one_or_none()
