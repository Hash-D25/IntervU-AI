"""Dashboard dependency wiring."""

from typing import Annotated

from fastapi import Depends

from app.core.container import SessionDep
from app.features.dashboard.service import DashboardService
from app.features.interview.repository import InterviewRepository


def get_interview_repository_for_dashboard(session: SessionDep) -> InterviewRepository:
    return InterviewRepository(session)


def get_dashboard_service(
    session: SessionDep,
    interviews: Annotated[InterviewRepository, Depends(get_interview_repository_for_dashboard)],
) -> DashboardService:
    return DashboardService(session, interviews)


DashboardServiceDep = Annotated[DashboardService, Depends(get_dashboard_service)]
