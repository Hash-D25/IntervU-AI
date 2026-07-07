"""Persistence for answer evaluations."""

from uuid import UUID

from sqlalchemy import select

from app.db.repository import BaseRepository
from app.features.evaluation.models import AnswerEvaluation


class AnswerEvaluationRepository(BaseRepository[AnswerEvaluation]):
    model = AnswerEvaluation

    async def get_for_answer(self, answer_id: UUID) -> AnswerEvaluation | None:
        result = await self.session.execute(
            select(AnswerEvaluation).where(AnswerEvaluation.answer_id == answer_id)
        )
        return result.scalar_one_or_none()

    async def get_for_question(self, question_id: UUID) -> AnswerEvaluation | None:
        from app.features.interview.models import Answer

        result = await self.session.execute(
            select(AnswerEvaluation)
            .join(Answer, Answer.id == AnswerEvaluation.answer_id)
            .where(Answer.question_id == question_id)
        )
        return result.scalar_one_or_none()
