"""Job description analyzer contract — implement a new strategy by satisfying this Protocol."""

from typing import Protocol

from app.features.job_description.processing.schemas import ParsedJobDescription


class JobDescriptionAnalyzer(Protocol):
    @property
    def name(self) -> str: ...

    async def analyze(self, text: str) -> ParsedJobDescription: ...
