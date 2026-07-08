"""Follow-up generation contracts."""

from typing import Protocol, runtime_checkable

from app.features.interview.follow_up.schemas import (
    ExtractedClaim,
    FollowUpContext,
    GeneratedFollowUp,
)


@runtime_checkable
class ClaimExtractor(Protocol):
    name: str

    async def extract(self, context: FollowUpContext) -> list[ExtractedClaim]: ...


@runtime_checkable
class FollowUpGenerator(Protocol):
    name: str

    async def generate(
        self,
        context: FollowUpContext,
        *,
        claims: list[ExtractedClaim],
    ) -> GeneratedFollowUp | None: ...
