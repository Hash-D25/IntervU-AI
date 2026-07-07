"""Resume parser contract — implement a new strategy by satisfying this Protocol."""

from typing import Protocol

from app.features.resume.parsing.progress import ParseProgressCallback
from app.features.resume.parsing.schemas import ParsedResume


class ResumeParser(Protocol):
    @property
    def name(self) -> str: ...

    async def parse(
        self,
        pdf_bytes: bytes,
        *,
        on_progress: ParseProgressCallback | None = None,
    ) -> ParsedResume: ...
