"""Feedback report orchestration."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestError, NotFoundError
from app.features.feedback.context_builder import build_feedback_context
from app.features.feedback.models import FeedbackReport
from app.features.feedback.protocols import FeedbackGenerator
from app.features.feedback.repository import FeedbackReportRepository
from app.features.feedback.schemas import FeedbackResult
from app.features.interview.models import Interview
from app.features.interview.repository import InterviewRepository


class FeedbackService:
    def __init__(
        self,
        session: AsyncSession,
        interviews: InterviewRepository,
        reports: FeedbackReportRepository,
        generator: FeedbackGenerator,
    ) -> None:
        self._session = session
        self._interviews = interviews
        self._reports = reports
        self._generator = generator

    async def generate_for_interview(
        self,
        *,
        user_id: UUID,
        interview_id: UUID,
    ) -> FeedbackResult:
        interview = await self._load_interview(interview_id, user_id)
        try:
            context = build_feedback_context(interview)
        except ValueError as exc:
            raise BadRequestError(str(exc)) from exc

        result = await self._generator.generate(context)
        result.generator_name = self._generator.name
        await self._persist_report(interview_id, result)
        await self._session.commit()
        return result

    async def get_for_interview(
        self,
        *,
        user_id: UUID,
        interview_id: UUID,
    ) -> FeedbackResult:
        interview = await self._load_interview(interview_id, user_id)
        report = await self._reports.get_for_interview(interview.id)
        if report is None:
            raise NotFoundError("Feedback report not found")
        return _entity_to_result(report)

    async def _persist_report(self, interview_id: UUID, result: FeedbackResult) -> None:
        existing = await self._reports.get_for_interview(interview_id)
        if existing is not None:
            existing.summary = result.summary
            existing.strengths = result.strengths
            existing.weaknesses = result.weaknesses
            existing.suggestions = result.recommendations
            existing.roadmap = result.learning_roadmap
            existing.overall_score = result.overall_score
            await self._session.flush()
            return
        await self._reports.add(
            FeedbackReport(
                interview_id=interview_id,
                summary=result.summary,
                strengths=result.strengths,
                weaknesses=result.weaknesses,
                suggestions=result.recommendations,
                roadmap=result.learning_roadmap,
                overall_score=result.overall_score,
            )
        )

    async def _load_interview(self, interview_id: UUID, user_id: UUID) -> Interview:
        interview = await self._interviews.get_for_user(interview_id, user_id)
        if interview is None:
            raise NotFoundError("Interview not found")
        return interview


def _entity_to_result(report: FeedbackReport) -> FeedbackResult:
    return FeedbackResult(
        summary=report.summary,
        strengths=report.strengths,
        weaknesses=report.weaknesses,
        recommendations=report.suggestions,
        learning_roadmap=report.roadmap,
        overall_score=report.overall_score or 0.0,
        generator_name="stored",
    )
