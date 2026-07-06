"""Resume upload orchestration.

The service validates uploads, delegates file I/O to ``FileStorageService``,
persists metadata via ``ResumeRepository``, and owns the commit boundary.
"""

from uuid import UUID

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.exceptions import NotFoundError
from app.features.resume.models import Resume
from app.features.resume.repository import ResumeRepository
from app.features.resume.storage import FileStorageService
from app.features.resume.validators import (
    PDF_CONTENT_TYPE,
    read_upload_with_size_limit,
    validate_pdf_content,
)
from app.features.user.models import User


class ResumeService:
    def __init__(
        self,
        session: AsyncSession,
        repository: ResumeRepository,
        storage: FileStorageService,
        settings: Settings,
    ) -> None:
        self._session = session
        self._repository = repository
        self._storage = storage
        self._max_bytes = settings.resume_max_size_mb * 1024 * 1024

    async def upload(self, user: User, upload_file: UploadFile) -> Resume:
        content = await read_upload_with_size_limit(upload_file, self._max_bytes)
        validate_pdf_content(content, upload_file.content_type)

        stored_path: str | None = None
        try:
            stored = await self._storage.save(user_id=user.id, content=content)
            stored_path = stored.key
            resume = await self._repository.add(
                Resume(
                    user_id=user.id,
                    original_filename=upload_file.filename or "resume.pdf",
                    stored_path=stored.key,
                    file_size_bytes=len(content),
                    content_type=PDF_CONTENT_TYPE,
                )
            )
            await self._session.commit()
            return resume
        except Exception:
            await self._session.rollback()
            if stored_path is not None:
                await self._storage.delete(stored_path)
            raise

    async def list_for_user(self, user_id: UUID) -> list[Resume]:
        return list(await self._repository.list_for_user(user_id))

    async def get_for_user(self, resume_id: UUID, user_id: UUID) -> Resume:
        resume = await self._repository.get_for_user(resume_id, user_id)
        if resume is None:
            raise NotFoundError("Resume not found")
        return resume

    async def delete(self, resume_id: UUID, user_id: UUID) -> None:
        resume = await self.get_for_user(resume_id, user_id)
        stored_path = resume.stored_path
        await self._repository.delete(resume)
        await self._session.commit()
        await self._storage.delete(stored_path)
