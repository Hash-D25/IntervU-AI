"""No-op claim extractor and follow-up generator (disable path)."""

from app.features.interview.follow_up.schemas import (
    ExtractedClaim,
    FollowUpContext,
    GeneratedFollowUp,
)


class NoOpClaimExtractor:
    name = "none"

    async def extract(self, context: FollowUpContext) -> list[ExtractedClaim]:
        return []


class NoOpFollowUpGenerator:
    name = "none"

    async def generate(
        self,
        context: FollowUpContext,
        *,
        claims: list[ExtractedClaim],
    ) -> GeneratedFollowUp | None:
        return None
