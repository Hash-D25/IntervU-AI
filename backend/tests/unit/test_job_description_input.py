"""Job description input normalization tests."""

import pytest

from app.core.exceptions import BadRequestError
from app.features.job_description.processing.input import (
    MIN_TEXT_LENGTH,
    extract_job_description_text_from_pdf,
    normalize_job_description_text,
)

MINIMAL_PDF = b"%PDF-1.4\n%%EOF"


def test_normalize_job_description_text_accepts_valid_input() -> None:
    text = "Senior Engineer " * 10
    assert len(normalize_job_description_text(text)) >= MIN_TEXT_LENGTH


def test_normalize_job_description_text_rejects_short_input() -> None:
    with pytest.raises(BadRequestError, match="at least"):
        normalize_job_description_text("too short")


def test_extract_job_description_text_from_pdf_rejects_empty_pdf() -> None:
    with pytest.raises(BadRequestError, match="Could not extract text"):
        extract_job_description_text_from_pdf(MINIMAL_PDF)
