"""Transcription context builder tests."""

from app.features.interview.planning.schemas import InterviewMetadata, InterviewType, ResumeSummary
from app.features.voice.context_builder import build_transcription_context


def test_build_transcription_context_includes_resume_terms() -> None:
    metadata = InterviewMetadata(
        company_name="EPAM",
        target_role="SDE intern",
        interview_type=InterviewType.TECHNICAL,
        has_job_description=False,
        resume_summary=ResumeSummary(
            skills=["Python"],
            technologies=["FastAPI", "PostgreSQL"],
            project_names=["UncDoIt", "ytNotes"],
            experience_titles=["Intern at Tulifo AI"],
        ),
        context_sources=["parsed_resume"],
    )

    context = build_transcription_context(metadata)

    assert "EPAM" in context.initial_prompt
    assert "FastAPI" in context.hint_terms
    assert "UncDoIt" in context.hint_terms
    assert "LeetCode" in context.hint_terms
