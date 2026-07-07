"""Interview planner contract."""

from typing import Protocol

from app.features.interview.planning.schemas import InterviewBlueprint, InterviewType
from app.features.resume.parsing.schemas import ParsedResume


class InterviewPlanner(Protocol):
    @property
    def name(self) -> str: ...

    async def build_plan(
        self,
        parsed_resume: ParsedResume,
        *,
        company_name: str,
        target_role: str,
        interview_type: InterviewType,
        job_description: str | None = None,
    ) -> InterviewBlueprint: ...
