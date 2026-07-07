"""Evaluation feature dependency wiring."""

from typing import Annotated

from fastapi import Depends

from app.core.container import SessionDep, SettingsDep
from app.features.evaluation.factory import create_answer_evaluator
from app.features.evaluation.protocols import AnswerEvaluator
from app.features.evaluation.repository import AnswerEvaluationRepository
from app.features.evaluation.service import AnswerEvaluationService
from app.features.interview.repository import InterviewRepository


def get_answer_evaluation_repository(session: SessionDep) -> AnswerEvaluationRepository:
    return AnswerEvaluationRepository(session)


def get_answer_evaluator(settings: SettingsDep) -> AnswerEvaluator:
    return create_answer_evaluator(settings)


def get_interview_repository_for_evaluation(session: SessionDep) -> InterviewRepository:
    return InterviewRepository(session)


def get_answer_evaluation_service(
    session: SessionDep,
    evaluations: Annotated[AnswerEvaluationRepository, Depends(get_answer_evaluation_repository)],
    interviews: Annotated[
        InterviewRepository, Depends(get_interview_repository_for_evaluation)
    ],
    evaluator: Annotated[AnswerEvaluator, Depends(get_answer_evaluator)],
) -> AnswerEvaluationService:
    return AnswerEvaluationService(session, evaluations, interviews, evaluator)


AnswerEvaluationServiceDep = Annotated[
    AnswerEvaluationService, Depends(get_answer_evaluation_service)
]
