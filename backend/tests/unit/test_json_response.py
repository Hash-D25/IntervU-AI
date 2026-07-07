"""JSON response parsing unit tests."""

import pytest

from app.core.exceptions import ParseError
from app.features.resume.parsing.json_response import parse_llm_json_response
from app.shared.llm_json import extract_json_payload, strip_code_fence


def test_strip_code_fence() -> None:
    raw = '```json\n{"skills": ["Python"]}\n```'
    assert strip_code_fence(raw) == '{"skills": ["Python"]}'


def test_parse_llm_json_response_validates_schema() -> None:
    parsed = parse_llm_json_response('{"skills": ["Python"], "technologies": []}')
    assert parsed.skills == ["Python"]


def test_parse_llm_json_response_rejects_invalid_json() -> None:
    with pytest.raises(ParseError, match="invalid resume JSON"):
        parse_llm_json_response("not-json")


def test_extract_json_payload_finds_object_in_prose() -> None:
    raw = 'Here is the data:\n{"skills": ["Go"], "technologies": []}\nThanks.'
    assert '"Go"' in extract_json_payload(raw)


def test_extract_json_payload_strips_thinking_block() -> None:
    raw = (
        "\nlong reasoning here\n\n"
        '{"skills": ["Rust"], "technologies": [], "projects": [], '
        '"experience": [], "education": []}'
    )
    parsed = parse_llm_json_response(raw)
    assert parsed.skills == ["Rust"]
