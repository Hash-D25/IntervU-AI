"""Answer evaluation orchestration."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.features.evaluation.models import AnswerEvaluation
from app.features.evaluation.protocols import AnswerEvaluator
from app.features.evaluation.repository import AnswerEvaluationRepository
from app.features.evaluation.schemas import AnswerEvaluationResult, EvaluationContext
from app.features.interview.execution.schemas import SessionQuestion
from app.features.interview.models import Interview
from app.features.interview.planning.schemas import InterviewMetadata
from app.features.interview.repository import InterviewRepository


class AnswerEvaluationService:
    def __init__(
        self,
        session: AsyncSession,
        evaluations: AnswerEvaluationRepository,
        interviews: InterviewRepository,
        evaluator: AnswerEvaluator,
    ) -> None:
        self._session = session
        self._evaluations = evaluations
        self._interviews = interviews
        self._evaluator = evaluator

    async def evaluate(
        self,
        context: EvaluationContext,
    ) -> AnswerEvaluationResult:
        result = await self._evaluator.evaluate(context)
        result.evaluator_name = self._evaluator.name
        return result

    async def evaluate_and_persist(
        self,
        *,
        answer_id: UUID,
        context: EvaluationContext,
    ) -> AnswerEvaluationResult:
        result = await self.evaluate(context)
        existing = await self._evaluations.get_for_answer(answer_id)
        if existing is not None:
            existing.overall_score = result.overall_score
            existing.scores = [score.model_dump(mode="json") for score in result.scores]
            existing.strengths = result.strengths
            existing.improvements = result.improvements
            existing.evaluator_name = result.evaluator_name
            await self._session.flush()
            return result
        await self._evaluations.add(
            AnswerEvaluation(
                answer_id=answer_id,
                overall_score=result.overall_score,
                scores=[score.model_dump(mode="json") for score in result.scores],
                strengths=result.strengths,
                improvements=result.improvements,
                evaluator_name=result.evaluator_name,
            )
        )
        return result

    async def get_for_question(
        self,
        *,
        user_id: UUID,
        interview_id: UUID,
        question_id: UUID,
    ) -> AnswerEvaluationResult:
        interview = await self._interviews.get_for_user(interview_id, user_id)
        if interview is None:
            raise NotFoundError("Interview not found")
        entity = await self._evaluations.get_for_question(question_id)
        if entity is None:
            raise NotFoundError("Answer evaluation not found")
        return _entity_to_result(entity)

    @staticmethod
    def build_context(
        *,
        interview: Interview,
        question: SessionQuestion,
        transcript: str,
    ) -> EvaluationContext:
        metadata = InterviewMetadata.model_validate(interview.interview_metadata)
        return EvaluationContext(
            question_text=question.text,
            answer_transcript=transcript,
            category=question.category,
            phase=question.phase.value,
            difficulty=question.difficulty,
            expected_topics=question.expected_topics,
            evaluation_rubric=question.evaluation_rubric,
            company_name=metadata.company_name,
            target_role=metadata.target_role,
        )


def _entity_to_result(entity: AnswerEvaluation) -> AnswerEvaluationResult:
    return AnswerEvaluationResult.model_validate(
        {
            "scores": entity.scores,
            "overall_score": entity.overall_score,
            "strengths": entity.strengths,
            "improvements": entity.improvements,
            "evaluator_name": entity.evaluator_name,
        }
    )
