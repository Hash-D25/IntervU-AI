"""PDF upload validation helpers."""

from fastapi import UploadFile

from app.core.exceptions import BadRequestError, PayloadTooLargeError

PDF_MAGIC = b"%PDF-"
PDF_CONTENT_TYPE = "application/pdf"
_READ_CHUNK_SIZE = 64 * 1024


async def read_upload_with_size_limit(upload_file: UploadFile, max_bytes: int) -> bytes:
    """Read an upload in chunks, rejecting empty or oversized payloads."""
    chunks: list[bytes] = []
    total = 0

    while chunk := await upload_file.read(_READ_CHUNK_SIZE):
        total += len(chunk)
        if total > max_bytes:
            raise PayloadTooLargeError(
                f"File exceeds the maximum size of {max_bytes // (1024 * 1024)} MB"
            )
        chunks.append(chunk)

    if total == 0:
        raise BadRequestError("Uploaded file is empty")

    return b"".join(chunks)


def validate_pdf_content(content: bytes, content_type: str | None) -> None:
    """Ensure the payload looks like a PDF (magic bytes + MIME when provided)."""
    if not content.startswith(PDF_MAGIC):
        raise BadRequestError("Only PDF files are allowed")

    if content_type is not None and content_type != PDF_CONTENT_TYPE:
        raise BadRequestError("Only PDF files are allowed")
