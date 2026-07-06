"""Map ORM resume rows to API responses."""

from app.core.config import Settings
from app.features.resume.models import Resume
from app.features.resume.schemas import ResumeResponse
from app.features.resume.storage import build_cloudinary_file_url


def to_resume_response(resume: Resume, settings: Settings) -> ResumeResponse:
    file_url = (
        build_cloudinary_file_url(resume.stored_path, settings)
        if settings.resume_storage_backend == "cloudinary"
        else None
    )
    return ResumeResponse(
        id=resume.id,
        user_id=resume.user_id,
        original_filename=resume.original_filename,
        stored_path=resume.stored_path,
        file_url=file_url,
        file_size_bytes=resume.file_size_bytes,
        content_type=resume.content_type,
        created_at=resume.created_at,
    )
