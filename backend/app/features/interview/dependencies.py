"""Interview feature dependency wiring."""

from typing import Annotated

from fastapi import Depends

from app.core.container import SessionDep, SettingsDep
from app.features.evaluation.dependencies import AnswerEvaluationServiceDep
from app.features.interview.execution.question_provider import PhaseQuestionProvider
from app.features.interview.execution.service import InterviewExecutionService
from app.features.interview.follow_up.factory import (
    create_claim_extractor,
    create_follow_up_generator,
)
from app.features.interview.follow_up.service import FollowUpService, parse_allowed_phases
from app.features.interview.memory.factory import create_memory_builder
from app.features.interview.memory.protocols import InterviewMemoryBuilder
from app.features.interview.planning.factory import create_interview_planner
from app.features.interview.planning.protocols import InterviewPlanner
from app.features.interview.question_generation.factory import create_question_generator_strategies
from app.features.interview.repository import (
    AnswerRepository,
    InterviewRepository,
    QuestionRepository,
)
from app.features.interview.service import InterviewService
from app.features.resume.parsed_repository import ResumeParsedProfileRepository
from app.features.resume.repository import ResumeRepository


def get_interview_repository(session: SessionDep) -> InterviewRepository:
    return InterviewRepository(session)


def get_question_repository(session: SessionDep) -> QuestionRepository:
    return QuestionRepository(session)


def get_answer_repository(session: SessionDep) -> AnswerRepository:
    return AnswerRepository(session)


def get_resume_repository(session: SessionDep) -> ResumeRepository:
    return ResumeRepository(session)


def get_parsed_resume_repository(session: SessionDep) -> ResumeParsedProfileRepository:
    return ResumeParsedProfileRepository(session)


def get_interview_planner() -> InterviewPlanner:
    return create_interview_planner()


def get_phase_question_provider(settings: SettingsDep) -> PhaseQuestionProvider:
    strategies = create_question_generator_strategies(settings)
    return PhaseQuestionProvider(strategies)


def get_follow_up_service(settings: SettingsDep) -> FollowUpService:
    return FollowUpService(
        create_claim_extractor(settings),
        create_follow_up_generator(settings),
        max_follow_ups_per_answer=settings.max_follow_ups_per_answer,
        max_follow_ups_per_interview=settings.max_follow_ups_per_interview,
        allowed_phases=parse_allowed_phases(settings.follow_up_on_phases),
    )


def get_memory_builder(settings: SettingsDep) -> InterviewMemoryBuilder:
    return create_memory_builder(settings)


def get_interview_service(
    session: SessionDep,
    interviews: Annotated[InterviewRepository, Depends(get_interview_repository)],
    resumes: Annotated[ResumeRepository, Depends(get_resume_repository)],
    parsed_resumes: Annotated[ResumeParsedProfileRepository, Depends(get_parsed_resume_repository)],
    planner: Annotated[InterviewPlanner, Depends(get_interview_planner)],
) -> InterviewService:
    return InterviewService(session, interviews, resumes, parsed_resumes, planner)


def get_interview_execution_service(
    session: SessionDep,
    interviews: Annotated[InterviewRepository, Depends(get_interview_repository)],
    questions: Annotated[QuestionRepository, Depends(get_question_repository)],
    answers: Annotated[AnswerRepository, Depends(get_answer_repository)],
    parsed_resumes: Annotated[ResumeParsedProfileRepository, Depends(get_parsed_resume_repository)],
    question_provider: Annotated[PhaseQuestionProvider, Depends(get_phase_question_provider)],
    evaluation_service: AnswerEvaluationServiceDep,
    follow_up_service: Annotated[FollowUpService, Depends(get_follow_up_service)],
    memory_builder: Annotated[InterviewMemoryBuilder, Depends(get_memory_builder)],
) -> InterviewExecutionService:
    return InterviewExecutionService(
        session,
        interviews,
        questions,
        answers,
        parsed_resumes,
        question_provider,
        evaluation_service,
        follow_up_service,
        memory_builder,
    )


InterviewServiceDep = Annotated[InterviewService, Depends(get_interview_service)]
InterviewExecutionServiceDep = Annotated[
    InterviewExecutionService, Depends(get_interview_execution_service)
]
