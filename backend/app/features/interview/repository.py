"""Persistence for the interview aggregate."""

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.repository import BaseRepository
from app.features.interview.models import Answer, Interview, Question


class InterviewRepository(BaseRepository[Interview]):
    model = Interview

    async def list_for_user(
        self, user_id: UUID, *, limit: int = 100, offset: int = 0
    ) -> Sequence[Interview]:
        result = await self.session.execute(
            select(Interview)
            .where(Interview.user_id == user_id)
            .order_by(Interview.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()

    async def list_for_user_with_feedback(
        self, user_id: UUID, *, limit: int = 100, offset: int = 0
    ) -> Sequence[Interview]:
        result = await self.session.execute(
            select(Interview)
            .options(selectinload(Interview.feedback_report))
            .where(Interview.user_id == user_id)
            .order_by(Interview.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()

    async def get_for_user(self, interview_id: UUID, user_id: UUID) -> Interview | None:
        result = await self.session.execute(
            select(Interview).where(Interview.id == interview_id, Interview.user_id == user_id)
        )
        return result.scalar_one_or_none()


class QuestionRepository(BaseRepository[Question]):
    model = Question

    async def list_for_interview(self, interview_id: UUID) -> Sequence[Question]:
        result = await self.session.execute(
            select(Question)
            .where(Question.interview_id == interview_id)
            .order_by(Question.position)
        )
        return result.scalars().all()


class AnswerRepository(BaseRepository[Answer]):
    model = Answer

    async def get_for_question(self, question_id: UUID) -> Answer | None:
        result = await self.session.execute(select(Answer).where(Answer.question_id == question_id))
        return result.scalar_one_or_none()
