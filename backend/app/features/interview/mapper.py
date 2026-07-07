"""Map interview domain models to API DTOs."""

from app.features.interview.models import Interview
from app.features.interview.planning.schemas import (
    InterviewMetadata,
    InterviewPlan,
    SessionState,
)
from app.features.interview.planning.state_machine import build_state_snapshot
from app.features.interview.schemas import InterviewResponse


def to_interview_response(interview: Interview) -> InterviewResponse:
    metadata = InterviewMetadata.model_validate(interview.interview_metadata)
    plan = InterviewPlan.model_validate(interview.interview_plan)
    session_state = build_state_snapshot(interview.session_state or SessionState.READY)
    return InterviewResponse(
        id=interview.id,
        user_id=interview.user_id,
        resume_id=interview.resume_id,
        company_name=interview.company,
        target_role=interview.role,
        interview_type=interview.interview_type,
        status=interview.status,
        session_state=session_state,
        interview_metadata=metadata,
        interview_plan=plan,
        job_description=interview.job_description,
        created_at=interview.created_at,
        updated_at=interview.updated_at,
    )
