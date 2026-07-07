"""Map parsed profile ORM rows to API responses."""

from app.features.resume.parsed_models import ResumeParsedProfile
from app.features.resume.parsing.schemas import EducationEntry, ExperienceEntry, ProjectEntry
from app.features.resume.schemas import ParsedProfileResponse


def to_parsed_profile_response(profile: ResumeParsedProfile) -> ParsedProfileResponse:
    return ParsedProfileResponse(
        resume_id=profile.resume_id,
        skills=profile.skills,
        projects=[ProjectEntry.model_validate(item) for item in profile.projects],
        experience=[ExperienceEntry.model_validate(item) for item in profile.experience],
        technologies=profile.technologies,
        education=[EducationEntry.model_validate(item) for item in profile.education],
        achievements=profile.achievements,
        parser_name=profile.parser_name,
        parse_status=profile.parse_status,
        parse_error=profile.parse_error,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )
