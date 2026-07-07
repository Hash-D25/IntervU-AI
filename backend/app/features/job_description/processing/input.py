"""Normalize and validate job description input from text or PDF."""

from app.core.exceptions import BadRequestError
from app.shared.pdf_text import extract_text_from_pdf

MIN_TEXT_LENGTH = 50
MAX_TEXT_LENGTH = 50_000


def normalize_job_description_text(text: str) -> str:
    cleaned = text.strip()
    if len(cleaned) < MIN_TEXT_LENGTH:
        raise BadRequestError(
            f"Job description must be at least {MIN_TEXT_LENGTH} characters after trimming"
        )
    if len(cleaned) > MAX_TEXT_LENGTH:
        raise BadRequestError(
            f"Job description must be at most {MAX_TEXT_LENGTH} characters"
        )
    return cleaned


def extract_job_description_text_from_pdf(pdf_bytes: bytes) -> str:
    return normalize_job_description_text(extract_text_from_pdf(pdf_bytes))
