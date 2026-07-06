"""PDF validation unit tests."""

import pytest

from app.core.exceptions import BadRequestError, PayloadTooLargeError
from app.features.resume.validators import read_upload_with_size_limit, validate_pdf_content

MINIMAL_PDF = b"%PDF-1.4\n%%EOF"


class _InMemoryUpload:
    def __init__(self, content: bytes, chunk_size: int = 1024) -> None:
        self._content = content
        self._chunk_size = chunk_size
        self._offset = 0

    async def read(self, size: int = -1) -> bytes:
        if self._offset >= len(self._content):
            return b""
        read_size = self._chunk_size if size < 0 else size
        chunk = self._content[self._offset : self._offset + read_size]
        self._offset += len(chunk)
        return chunk


async def test_validate_pdf_content_accepts_valid_pdf() -> None:
    validate_pdf_content(MINIMAL_PDF, "application/pdf")


def test_validate_pdf_content_rejects_non_pdf_magic() -> None:
    with pytest.raises(BadRequestError, match="Only PDF"):
        validate_pdf_content(b"not-a-pdf", "application/pdf")


def test_validate_pdf_content_rejects_wrong_content_type() -> None:
    with pytest.raises(BadRequestError, match="Only PDF"):
        validate_pdf_content(MINIMAL_PDF, "text/plain")


async def test_read_upload_rejects_empty_file() -> None:
    with pytest.raises(BadRequestError, match="empty"):
        await read_upload_with_size_limit(_InMemoryUpload(b""), max_bytes=1024)  # type: ignore[arg-type]


async def test_read_upload_rejects_oversized_file() -> None:
    upload = _InMemoryUpload(MINIMAL_PDF + b"x" * 2048, chunk_size=512)
    with pytest.raises(PayloadTooLargeError):
        await read_upload_with_size_limit(upload, max_bytes=1024)  # type: ignore[arg-type]
