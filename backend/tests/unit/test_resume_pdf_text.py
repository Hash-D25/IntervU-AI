"""PDF text extraction unit tests."""

import pytest

from app.core.exceptions import BadRequestError
from app.features.resume.parsing.pdf_text import extract_text_from_pdf

MINIMAL_PDF = b"%PDF-1.4\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF"


def test_extract_text_rejects_unreadable_pdf() -> None:
    with pytest.raises(BadRequestError, match="Could not extract text"):
        extract_text_from_pdf(MINIMAL_PDF)
