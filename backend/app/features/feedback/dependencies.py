"""Feedback feature dependency wiring."""

from typing import Annotated

from fastapi import Depends

from app.core.container import SessionDep, SettingsDep
from app.features.feedback.factory import create_feedback_generator
from app.features.feedback.protocols import FeedbackGenerator
from app.features.feedback.repository import FeedbackReportRepository
from app.features.feedback.service import FeedbackService
from app.features.interview.repository import InterviewRepository


def get_feedback_report_repository(session: SessionDep) -> FeedbackReportRepository:
    return FeedbackReportRepository(session)


def get_interview_repository_for_feedback(session: SessionDep) -> InterviewRepository:
    return InterviewRepository(session)


def get_feedback_generator(settings: SettingsDep) -> FeedbackGenerator:
    return create_feedback_generator(settings)


def get_feedback_service(
    session: SessionDep,
    interviews: Annotated[InterviewRepository, Depends(get_interview_repository_for_feedback)],
    reports: Annotated[FeedbackReportRepository, Depends(get_feedback_report_repository)],
    generator: Annotated[FeedbackGenerator, Depends(get_feedback_generator)],
) -> FeedbackService:
    return FeedbackService(session, interviews, reports, generator)


FeedbackServiceDep = Annotated[FeedbackService, Depends(get_feedback_service)]
