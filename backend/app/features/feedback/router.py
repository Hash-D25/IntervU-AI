"""Feedback API routes."""

from uuid import UUID

from fastapi import APIRouter, status

from app.features.auth.dependencies import CurrentUserDep
from app.features.feedback.dependencies import FeedbackServiceDep
from app.features.feedback.schemas import FeedbackResult

router = APIRouter(prefix="/interviews", tags=["feedback"])


@router.post(
    "/{interview_id}/feedback/generate",
    response_model=FeedbackResult,
    status_code=status.HTTP_201_CREATED,
)
async def generate_feedback(
    interview_id: UUID,
    current_user: CurrentUserDep,
    service: FeedbackServiceDep,
) -> FeedbackResult:
    return await service.generate_for_interview(
        user_id=current_user.id,
        interview_id=interview_id,
    )


@router.get("/{interview_id}/feedback", response_model=FeedbackResult)
async def get_feedback(
    interview_id: UUID,
    current_user: CurrentUserDep,
    service: FeedbackServiceDep,
) -> FeedbackResult:
    return await service.get_for_interview(
        user_id=current_user.id,
        interview_id=interview_id,
    )
