"""Select claim extractor / follow-up generator from configuration."""

from app.core.config import Settings
from app.core.exceptions import BadRequestError
from app.features.interview.follow_up.protocols import ClaimExtractor, FollowUpGenerator
from app.features.interview.follow_up.strategies.llm_claim_extractor import (
    create_llm_claim_extractor,
)
from app.features.interview.follow_up.strategies.llm_follow_up_generator import (
    create_llm_follow_up_generator,
)
from app.features.interview.follow_up.strategies.noop import (
    NoOpClaimExtractor,
    NoOpFollowUpGenerator,
)


def create_claim_extractor(settings: Settings) -> ClaimExtractor:
    if settings.follow_up_generator == "none":
        return NoOpClaimExtractor()
    if settings.follow_up_generator == "llm":
        return create_llm_claim_extractor(settings)
    raise BadRequestError(f"Unsupported follow-up generator: {settings.follow_up_generator}")


def create_follow_up_generator(settings: Settings) -> FollowUpGenerator:
    if settings.follow_up_generator == "none":
        return NoOpFollowUpGenerator()
    if settings.follow_up_generator == "llm":
        return create_llm_follow_up_generator(settings)
    raise BadRequestError(f"Unsupported follow-up generator: {settings.follow_up_generator}")
