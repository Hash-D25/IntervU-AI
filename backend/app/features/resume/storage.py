"""Resume file storage — local disk and Cloudinary backends.

``FileStorageService`` is the boundary the upload service depends on. Swap
backends via ``RESUME_STORAGE_BACKEND`` without changing business logic.
"""

import asyncio
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol
from uuid import UUID

import cloudinary
import cloudinary.uploader
import cloudinary.utils

from app.core.config import Settings
from app.core.exceptions import BadRequestError


@dataclass(frozen=True, slots=True)
class StoredFile:
    """Storage reference returned by every backend."""

    key: str  # local relative path or Cloudinary public_id
    url: str | None  # secure URL when using Cloudinary


class FileStorageService(Protocol):
    async def save(self, *, user_id: UUID, content: bytes) -> StoredFile:
        """Persist content and return a storage reference."""
        ...

    async def delete(self, storage_key: str) -> None:
        """Remove a previously stored file if it exists."""
        ...


def configure_cloudinary(settings: Settings) -> None:
    cloudinary.config(
        cloud_name=settings.cloudinary_cloud_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )


def build_cloudinary_file_url(public_id: str, settings: Settings) -> str:
    configure_cloudinary(settings)
    url, _options = cloudinary.utils.cloudinary_url(public_id, resource_type="raw", secure=True)
    return str(url)


class LocalFileStorageService:
    def __init__(self, upload_root: str) -> None:
        self._root = Path(upload_root)

    async def save(self, *, user_id: UUID, content: bytes) -> StoredFile:
        relative_path = Path("resumes") / str(user_id) / f"{uuid.uuid4()}.pdf"
        absolute_path = self._root / relative_path
        absolute_path.parent.mkdir(parents=True, exist_ok=True)
        absolute_path.write_bytes(content)
        return StoredFile(key=relative_path.as_posix(), url=None)

    async def delete(self, storage_key: str) -> None:
        absolute_path = self._root / Path(storage_key)
        if absolute_path.is_file():
            absolute_path.unlink()


class CloudinaryFileStorageService:
    def __init__(self, settings: Settings) -> None:
        configure_cloudinary(settings)

    async def save(self, *, user_id: UUID, content: bytes) -> StoredFile:
        public_id = f"resumes/{user_id}/{uuid.uuid4()}"
        result = await asyncio.to_thread(
            cloudinary.uploader.upload,
            content,
            public_id=public_id,
            resource_type="raw",
            overwrite=False,
        )
        secure_url = result.get("secure_url")
        if not isinstance(secure_url, str):
            raise BadRequestError("Cloudinary upload did not return a secure URL")
        public_id_value = result.get("public_id", public_id)
        if not isinstance(public_id_value, str):
            public_id_value = public_id
        return StoredFile(key=public_id_value, url=secure_url)

    async def delete(self, storage_key: str) -> None:
        await asyncio.to_thread(
            cloudinary.uploader.destroy,
            storage_key,
            resource_type="raw",
            invalidate=True,
        )


def create_file_storage_service(settings: Settings) -> FileStorageService:
    if settings.resume_storage_backend == "cloudinary":
        if not (
            settings.cloudinary_cloud_name
            and settings.cloudinary_api_key
            and settings.cloudinary_api_secret
        ):
            raise ValueError(
                "Cloudinary credentials are required when RESUME_STORAGE_BACKEND=cloudinary"
            )
        return CloudinaryFileStorageService(settings)
    return LocalFileStorageService(settings.resume_upload_dir)
