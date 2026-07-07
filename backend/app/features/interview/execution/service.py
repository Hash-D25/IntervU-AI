"""Orchestrate interview execution with persistence and question generation."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestError, NotFoundError
from app.features.evaluation.schemas import AnswerEvaluationResult
from app.features.evaluation.service import AnswerEvaluationService
from app.features.interview.execution.engine import InterviewEngine
from app.features.interview.execution.project_selection import build_execution_hints
from app.features.interview.execution.question_provider import PhaseQuestionProvider
from app.features.interview.execution.schemas import (
    EngineSnapshot,
    EngineStatus,
    InterviewPhase,
    SessionContext,
    SessionQuestion,
)
from app.features.interview.models import Answer, Interview, InterviewStatus, Question, QuestionKind
from app.features.interview.planning.schemas import InterviewMetadata, InterviewPlan
from app.features.interview.question_generation.schemas import (
    QuestionCategory,
    QuestionGenerationContext,
)
from app.features.interview.repository import (
    AnswerRepository,
    InterviewRepository,
    QuestionRepository,
)
from app.features.resume.parsed_models import ParseStatus
from app.features.resume.parsed_repository import ResumeParsedProfileRepository
from app.features.resume.parsing.schemas import ParsedResume


class InterviewExecutionService:
    def __init__(
        self,
        session: AsyncSession,
        interviews: InterviewRepository,
        questions: QuestionRepository,
        answers: AnswerRepository,
        parsed_resumes: ResumeParsedProfileRepository,
        question_provider: PhaseQuestionProvider,
        evaluation_service: AnswerEvaluationService,
    ) -> None:
        self._session = session
        self._interviews = interviews
        self._questions = questions
        self._answers = answers
        self._parsed_resumes = parsed_resumes
        self._question_provider = question_provider
        self._evaluation_service = evaluation_service
        self._engine = InterviewEngine()

    async def get_snapshot(self, *, user_id: UUID, interview_id: UUID) -> EngineSnapshot:
        interview = await self._load_interview(interview_id, user_id)
        context = self._load_context(interview)
        return self._engine.snapshot(context)

    async def start(self, *, user_id: UUID, interview_id: UUID) -> EngineSnapshot:
        interview = await self._load_interview(interview_id, user_id)
        context = self._load_context(interview)
        if context.status != EngineStatus.NOT_STARTED:
            raise BadRequestError("Interview execution has already started")

        context = self._engine.start(context)
        context = await self._prepare_current_phase_question(interview, context)
        return await self._persist(interview, context)

    async def submit_answer(
        self,
        *,
        user_id: UUID,
        interview_id: UUID,
        transcript: str,
    ) -> EngineSnapshot:
        interview = await self._load_interview(interview_id, user_id)
        context = self._load_context(interview)
        current = context.questions[-1] if context.questions else None
        if current is None or current.id is None:
            raise BadRequestError("No current question to answer")

        context = self._engine.submit_answer(context, transcript)
        answer = await self._persist_answer(current.id, transcript)
        evaluation = await self._evaluation_service.evaluate_and_persist(
            answer_id=answer.id,
            context=AnswerEvaluationService.build_context(
                interview=interview,
                question=current,
                transcript=transcript,
            ),
        )
        context = self._attach_evaluation(context, current.id, evaluation)
        if context.status == EngineStatus.IN_PROGRESS and not context.awaiting_answer:
            context = await self._prepare_current_phase_question(interview, context)
        return await self._persist(interview, context)

    async def _prepare_current_phase_question(
        self,
        interview: Interview,
        context: SessionContext,
    ) -> SessionContext:
        if context.status != EngineStatus.IN_PROGRESS or context.phase is None:
            return context
        if context.phase == InterviewPhase.FINAL or context.awaiting_answer:
            return context

        generation_context = await self._build_generation_context(interview, context)
        position = len(context.questions)
        question = await self._question_provider.generate_for_phase(
            context.phase,
            company_name=context.company_name,
            target_role=context.target_role,
            position=position,
            generation_context=generation_context,
        )
        persisted = await self._persist_question(interview.id, question)
        question = question.model_copy(update={"id": persisted.id})
        return self._engine.attach_question(context, question)

    async def _persist(
        self,
        interview: Interview,
        context: SessionContext,
    ) -> EngineSnapshot:
        interview.execution_context = context.model_dump(mode="json")
        if context.status == EngineStatus.IN_PROGRESS:
            interview.status = InterviewStatus.IN_PROGRESS
        elif context.status == EngineStatus.COMPLETED:
            interview.status = InterviewStatus.COMPLETED
        await self._session.commit()
        await self._session.refresh(interview)
        return self._engine.snapshot(context)

    async def _persist_question(self, interview_id: UUID, question: SessionQuestion) -> Question:
        entity = Question(
            interview_id=interview_id,
            position=question.position,
            text=question.text,
            kind=_kind_for_category(question.category),
        )
        return await self._questions.add(entity)

    async def _persist_answer(self, question_id: UUID, transcript: str) -> Answer:
        existing = await self._answers.get_for_question(question_id)
        cleaned = transcript.strip()
        if existing is not None:
            existing.transcript = cleaned
            await self._session.flush()
            return existing
        return await self._answers.add(Answer(question_id=question_id, transcript=cleaned))

    @staticmethod
    def _attach_evaluation(
        context: SessionContext,
        question_id: UUID,
        evaluation: AnswerEvaluationResult,
    ) -> SessionContext:
        questions = [
            question.model_copy(update={"evaluation": evaluation})
            if question.id == question_id
            else question
            for question in context.questions
        ]
        return context.model_copy(update={"questions": questions})

    async def _build_generation_context(
        self,
        interview: Interview,
        session_context: SessionContext | None = None,
    ) -> QuestionGenerationContext:
        if interview.resume_id is None:
            raise BadRequestError("Interview is missing resume context")
        parsed_profile = await self._parsed_resumes.get_by_resume_id(interview.resume_id)
        if parsed_profile is None or parsed_profile.parse_status != ParseStatus.COMPLETED:
            raise BadRequestError("Resume must be parsed before running the interview")

        metadata = InterviewMetadata.model_validate(interview.interview_metadata)
        plan = InterviewPlan.model_validate(interview.interview_plan)
        resume = ParsedResume(
            skills=parsed_profile.skills,
            projects=parsed_profile.projects,
            experience=parsed_profile.experience,
            technologies=parsed_profile.technologies,
            education=parsed_profile.education,
            achievements=parsed_profile.achievements,
        )
        hints: dict[str, object] = {}
        if session_context is not None:
            hints = build_execution_hints(
                session=session_context,
                project_names=[project.name for project in resume.projects],
                experience_titles=[entry.title for entry in resume.experience],
            )
        return QuestionGenerationContext(
            company_name=metadata.company_name,
            target_role=metadata.target_role,
            interview_type=metadata.interview_type,
            interview_plan=plan,
            resume=resume,
            job_description_text=interview.job_description,
            **hints,
        )

    async def _load_interview(self, interview_id: UUID, user_id: UUID) -> Interview:
        interview = await self._interviews.get_for_user(interview_id, user_id)
        if interview is None:
            raise NotFoundError("Interview not found")
        return interview

    def _load_context(self, interview: Interview) -> SessionContext:
        raw = interview.execution_context or {}
        if raw:
            return SessionContext.model_validate(raw)
        metadata = InterviewMetadata.model_validate(interview.interview_metadata)
        return self._engine.build_context(
            interview_type=metadata.interview_type,
            company_name=metadata.company_name,
            target_role=metadata.target_role,
        )


def _kind_for_category(category: str) -> QuestionKind:
    if category == QuestionCategory.BEHAVIORAL.value:
        return QuestionKind.BEHAVIORAL
    return QuestionKind.TECHNICAL
