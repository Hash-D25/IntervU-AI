"""Deterministic interview planner seeded from a parsed resume."""

from app.features.interview.planning.schemas import (
    InterviewBlueprint,
    InterviewMetadata,
    InterviewPlan,
    InterviewType,
    ResumeSummary,
    SessionState,
)
from app.features.interview.planning.state_machine import build_state_snapshot
from app.features.resume.parsing.project_names import sanitize_project_name
from app.features.resume.parsing.schemas import ParsedResume


class ResumeBasedInterviewPlanner:
    name = "resume_based"

    async def build_plan(
        self,
        parsed_resume: ParsedResume,
        *,
        company_name: str,
        target_role: str,
        interview_type: InterviewType,
        job_description: str | None = None,
    ) -> InterviewBlueprint:
        resume_summary = ResumeSummary(
            skills=parsed_resume.skills[:8],
            technologies=parsed_resume.technologies[:8],
            project_names=[
                sanitize_project_name(project.name) for project in parsed_resume.projects[:4]
            ],
            experience_titles=[entry.title for entry in parsed_resume.experience[:4]],
        )
        focus_areas = _focus_areas(parsed_resume, interview_type, job_description)
        question_mix = _question_mix(interview_type, job_description)
        metadata = InterviewMetadata(
            company_name=company_name,
            target_role=target_role,
            interview_type=interview_type,
            has_job_description=bool(job_description and job_description.strip()),
            resume_summary=resume_summary,
            context_sources=_context_sources(job_description),
        )
        plan = InterviewPlan(
            focus_areas=focus_areas,
            question_mix=question_mix,
            estimated_rounds=3 if interview_type == InterviewType.MIXED else 2,
            follow_up_strategy=(
                "Ask targeted follow-ups on resume-backed claims and deepen "
                "based on answer quality."
            ),
            evaluation_axes=_evaluation_axes(interview_type, job_description),
        )
        return InterviewBlueprint(
            metadata=metadata,
            session_state=build_state_snapshot(SessionState.READY),
            interview_plan=plan,
        )


def _focus_areas(
    parsed_resume: ParsedResume, interview_type: InterviewType, job_description: str | None
) -> list[str]:
    focus = [*parsed_resume.skills[:4], *parsed_resume.technologies[:4]]
    if interview_type in {InterviewType.TECHNICAL, InterviewType.MIXED}:
        focus.append("problem solving")
    if interview_type in {InterviewType.BEHAVIORAL, InterviewType.MIXED}:
        focus.append("communication")
    if job_description and job_description.strip():
        focus.append("job-description alignment")
    return _dedupe(focus)[:8]


def _question_mix(interview_type: InterviewType, job_description: str | None) -> list[str]:
    if interview_type == InterviewType.TECHNICAL:
        mix = ["resume_deep_dive", "technical_core", "project_walkthrough"]
    elif interview_type == InterviewType.BEHAVIORAL:
        mix = ["resume_deep_dive", "behavioral", "collaboration"]
    else:
        mix = ["resume_deep_dive", "technical_core", "behavioral"]
    if job_description and job_description.strip():
        mix.append("job_alignment")
    return mix


def _evaluation_axes(interview_type: InterviewType, job_description: str | None) -> list[str]:
    axes = ["clarity", "depth", "evidence", "communication"]
    if interview_type != InterviewType.BEHAVIORAL:
        axes.append("technical_accuracy")
    if job_description and job_description.strip():
        axes.append("role_alignment")
    return _dedupe(axes)


def _context_sources(job_description: str | None) -> list[str]:
    sources = ["parsed_resume"]
    if job_description and job_description.strip():
        sources.append("job_description")
    return sources


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        key = value.casefold()
        if not value or key in seen:
            continue
        seen.add(key)
        result.append(value)
    return result
