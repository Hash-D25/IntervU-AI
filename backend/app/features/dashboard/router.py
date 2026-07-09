"""Dashboard routes."""

from fastapi import APIRouter

from app.features.auth.dependencies import CurrentUserDep
from app.features.dashboard.dependencies import DashboardServiceDep
from app.features.dashboard.schemas import DashboardSummary

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/", response_model=DashboardSummary)
async def get_dashboard(
    current_user: CurrentUserDep,
    service: DashboardServiceDep,
) -> DashboardSummary:
    return await service.get_summary(current_user.id)
