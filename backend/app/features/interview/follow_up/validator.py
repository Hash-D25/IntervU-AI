"""Validate and normalize follow-up output."""

import re

from app.core.exceptions import ParseError
from app.features.interview.follow_up.claim_filter import claim_grounded_in_answer
from app.features.interview.follow_up.schemas import ExtractedClaim, GeneratedFollowUp

_MULTI_SPACE = re.compile(r"\s+")
_MAX_CLAIMS = 4


class FollowUpValidator:
    @classmethod
    def validate_claims(
        cls,
        claims: list[ExtractedClaim],
        *,
        answer_transcript: str = "",
        question_text: str = "",
    ) -> list[ExtractedClaim]:
        cleaned: list[ExtractedClaim] = []
        seen: set[str] = set()
        for claim in claims:
            text = _MULTI_SPACE.sub(" ", claim.text.strip())
            probe = _MULTI_SPACE.sub(" ", claim.probe_angle.strip())
            if not text or not probe:
                continue
            if answer_transcript and not claim_grounded_in_answer(
                text,
                answer_transcript,
                question_text,
            ):
                continue
            key = text.casefold()
            if key in seen:
                continue
            seen.add(key)
            cleaned.append(
                ExtractedClaim(
                    text=text,
                    claim_type=claim.claim_type.strip() or "technical",
                    probe_angle=probe,
                )
            )
            if len(cleaned) >= _MAX_CLAIMS:
                break
        return cleaned

    @classmethod
    def validate_follow_up(
        cls,
        follow_up: GeneratedFollowUp,
        *,
        previous_follow_ups: list[str],
        answer_transcript: str = "",
        question_text: str = "",
    ) -> GeneratedFollowUp:
        text = _MULTI_SPACE.sub(" ", follow_up.text.strip())
        if not text:
            raise ParseError("Follow-up question cannot be empty")
        if not text.endswith("?"):
            text = f"{text}?"
        for previous in previous_follow_ups:
            if previous.strip().casefold() == text.casefold():
                raise ParseError("Follow-up duplicates a previous probe")
        claims = [
            _MULTI_SPACE.sub(" ", claim.strip())
            for claim in follow_up.probed_claims
            if claim.strip()
            and (
                not answer_transcript
                or claim_grounded_in_answer(claim, answer_transcript, question_text)
            )
        ]
        return GeneratedFollowUp(
            text=text,
            category=follow_up.category.strip() or "project",
            difficulty=follow_up.difficulty.strip() or "medium",
            expected_topics=[
                _MULTI_SPACE.sub(" ", topic.strip())
                for topic in follow_up.expected_topics
                if topic.strip()
            ][:6],
            evaluation_rubric=[
                _MULTI_SPACE.sub(" ", item.strip())
                for item in follow_up.evaluation_rubric
                if item.strip()
            ][:6]
            or ["depth", "reasoning"],
            probed_claims=claims[:4],
            generator_name=follow_up.generator_name.strip() or "llm",
        )
