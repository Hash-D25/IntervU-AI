"""Interview creation and retrieval routes."""

from uuid import UUID

from fastapi import APIRouter, status

from app.features.auth.dependencies import CurrentUserDep
from app.features.interview.dependencies import InterviewExecutionServiceDep, InterviewServiceDep
from app.features.interview.execution_mapper import to_execution_snapshot_response
from app.features.interview.mapper import to_interview_response
from app.features.interview.schemas import (
    CreateInterviewRequest,
    ExecutionSnapshotResponse,
    InterviewResponse,
    SubmitAnswerRequest,
)

router = APIRouter(prefix="/interviews", tags=["interviews"])


@router.post("/", response_model=InterviewResponse, status_code=status.HTTP_201_CREATED)
async def create_interview(
    current_user: CurrentUserDep,
    service: InterviewServiceDep,
    body: CreateInterviewRequest,
) -> InterviewResponse:
    interview = await service.create(
        user_id=current_user.id,
        resume_id=body.resume_id,
        company_name=body.company_name,
        target_role=body.target_role,
        interview_type=body.interview_type,
        job_description=body.job_description,
    )
    return to_interview_response(interview)


@router.get("/{interview_id}", response_model=InterviewResponse)
async def get_interview(
    interview_id: UUID,
    current_user: CurrentUserDep,
    service: InterviewServiceDep,
) -> InterviewResponse:
    interview = await service.get_for_user(interview_id, current_user.id)
    return to_interview_response(interview)


@router.get("/{interview_id}/execution", response_model=ExecutionSnapshotResponse)
async def get_execution_snapshot(
    interview_id: UUID,
    current_user: CurrentUserDep,
    execution_service: InterviewExecutionServiceDep,
) -> ExecutionSnapshotResponse:
    snapshot = await execution_service.get_snapshot(
        user_id=current_user.id,
        interview_id=interview_id,
    )
    return to_execution_snapshot_response(snapshot)


@router.post("/{interview_id}/execution/start", response_model=ExecutionSnapshotResponse)
async def start_interview_execution(
    interview_id: UUID,
    current_user: CurrentUserDep,
    execution_service: InterviewExecutionServiceDep,
) -> ExecutionSnapshotResponse:
    snapshot = await execution_service.start(
        user_id=current_user.id,
        interview_id=interview_id,
    )
    return to_execution_snapshot_response(snapshot)


@router.post("/{interview_id}/execution/answer", response_model=ExecutionSnapshotResponse)
async def submit_interview_answer(
    interview_id: UUID,
    current_user: CurrentUserDep,
    execution_service: InterviewExecutionServiceDep,
    body: SubmitAnswerRequest,
) -> ExecutionSnapshotResponse:
    snapshot = await execution_service.submit_answer(
        user_id=current_user.id,
        interview_id=interview_id,
        transcript=body.transcript,
    )
    return to_execution_snapshot_response(snapshot)

