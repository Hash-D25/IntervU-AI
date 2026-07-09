"""Synthesizer factory + FakeSynthesizer unit tests."""

import pytest

from app.ai.synthesis.base import SpeechSynthesizer
from app.ai.synthesis.factory import create_synthesizer
from app.ai.synthesis.strategies.fake_synthesizer import FakeSynthesizer
from app.core.config import Settings
from app.core.exceptions import BadRequestError


def _settings(**overrides: object) -> Settings:
    base = {
        "database_url": "postgresql+psycopg://u:p@localhost/db",
        **overrides,
    }
    return Settings(**base)  # type: ignore[arg-type]


def test_factory_returns_fake_synthesizer_by_default() -> None:
    synthesizer = create_synthesizer(_settings())
    assert isinstance(synthesizer, FakeSynthesizer)
    assert isinstance(synthesizer, SpeechSynthesizer)


def test_factory_rejects_unknown_synthesizer() -> None:
    with pytest.raises(BadRequestError, match="Unsupported synthesizer"):
        create_synthesizer(_settings(synthesizer="unknown"))


async def test_synthesize_returns_wav_payload() -> None:
    audio = await FakeSynthesizer().synthesize("Hello there")
    assert audio.content_type == "audio/wav"
    assert audio.sample_rate == 24_000
    assert audio.content.startswith(b"RIFF")
    assert len(audio.content) > 44  # WAV header + at least some samples


async def test_synthesize_stream_yields_reassemblable_chunks() -> None:
    synthesizer = FakeSynthesizer()
    chunks = [chunk async for chunk in synthesizer.synthesize_stream("Hello world")]
    assert chunks
    assert chunks[-1].is_final is True
    assert all(chunk.content_type == "audio/wav" for chunk in chunks)
    combined = b"".join(chunk.content for chunk in chunks)
    expected = (await synthesizer.synthesize("Hello world")).content
    assert combined == expected
