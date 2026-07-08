"""Parse LLM JSON for claim extraction and follow-up generation."""

import json
from typing import Any

from app.core.exceptions import ParseError
from app.features.interview.follow_up.schemas import ExtractedClaim, GeneratedFollowUp
from app.shared.llm_json import extract_json_payload


def parse_claims_response(raw_response: str) -> list[ExtractedClaim]:
    try:
        payload: dict[str, Any] = json.loads(extract_json_payload(raw_response))
        items = payload.get("claims", [])
        if not isinstance(items, list):
            raise ParseError("Claims payload must include a claims list")
        claims: list[ExtractedClaim] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            claims.append(ExtractedClaim.model_validate(item))
        return claims
    except (json.JSONDecodeError, ValueError) as exc:
        raise ParseError("LLM returned invalid claims JSON") from exc


def parse_follow_up_response(
    raw_response: str,
    *,
    fallback_category: str,
) -> GeneratedFollowUp:
    try:
        payload: dict[str, Any] = json.loads(extract_json_payload(raw_response))
        payload.setdefault("category", fallback_category)
        payload.setdefault("difficulty", "medium")
        payload.setdefault("expected_topics", [])
        payload.setdefault("evaluation_rubric", ["depth", "reasoning"])
        payload.setdefault("probed_claims", [])
        payload.setdefault("generator_name", "llm")
        if "question" in payload and "text" not in payload:
            payload["text"] = payload.pop("question")
        return GeneratedFollowUp.model_validate(payload)
    except (json.JSONDecodeError, ValueError) as exc:
        raise ParseError("LLM returned invalid follow-up JSON") from exc
