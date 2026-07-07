"""Extract plain text from PDF bytes."""

import io

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from app.core.exceptions import BadRequestError


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
    except PdfReadError as exc:
        raise BadRequestError("Could not extract text from PDF") from exc

    pages = [page.extract_text() or "" for page in reader.pages]
    text = "\n".join(pages).strip()
    if not text:
        raise BadRequestError("Could not extract text from PDF")
    return text
