"""Interview planner unit tests."""

from app.features.interview.planning.schemas import InterviewType
from app.features.interview.planning.strategies.resume_based_planner import (
    ResumeBasedInterviewPlanner,
)
from app.features.resume.parsing.schemas import (
    EducationEntry,
    ExperienceEntry,
    ParsedResume,
    ProjectEntry,
)


def _sample_resume() -> ParsedResume:
    return ParsedResume(
        skills=["Python", "FastAPI", "Communication"],
        projects=[ProjectEntry(name="InterviewerAI")],
        experience=[ExperienceEntry(title="Engineer", company="Acme")],
        technologies=["PostgreSQL", "Docker"],
        education=[EducationEntry(institution="Example University")],
        achievements=["Hackathon winner"],
    )


async def test_resume_based_planner_builds_blueprint_with_job_description() -> None:
    planner = ResumeBasedInterviewPlanner()
    blueprint = await planner.build_plan(
        _sample_resume(),
        company_name="EPAM",
        target_role="AI-Native Software Engineering Intern",
        interview_type=InterviewType.MIXED,
        job_description="Role requires AI-native engineering and coding fundamentals.",
    )

    assert blueprint.metadata.company_name == "EPAM"
    assert blueprint.metadata.has_job_description is True
    assert "job_description" in blueprint.metadata.context_sources
    assert blueprint.session_state.current == "ready"
    assert blueprint.interview_plan.focus_areas


async def test_resume_based_planner_sanitizes_project_names() -> None:
    planner = ResumeBasedInterviewPlanner()
    resume = ParsedResume(
        skills=["Python"],
        projects=[
            ProjectEntry(name="UncDoIt - AI W eb Navigation AssistantLink"),
            ProjectEntry(name="Social Media App Live"),
        ],
    )
    blueprint = await planner.build_plan(
        resume,
        company_name="EPAM",
        target_role="Intern",
        interview_type=InterviewType.TECHNICAL,
    )

    assert blueprint.metadata.resume_summary.project_names[0] == (
        "UncDoIt - AI Web Navigation Assistant"
    )
    assert blueprint.metadata.resume_summary.project_names[1] == "Social Media App"
