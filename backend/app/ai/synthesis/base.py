"""Provider-agnostic text-to-speech contract."""

from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass(frozen=True, slots=True)
class SynthesizedAudio:
    """Fully synthesized speech payload produced by the speech feature layer."""

    content: bytes
    content_type: str
    sample_rate: int


@dataclass(frozen=True, slots=True)
class AudioChunk:
    """A partial slice of synthesized audio yielded by a streaming synthesizer.

    Concatenating every chunk's ``content`` in order reproduces the full payload.
    """

    content: bytes
    content_type: str
    sample_rate: int
    is_final: bool = False


@runtime_checkable
class SpeechSynthesizer(Protocol):
    """Text-to-speech engine. Interview logic never depends on a concrete SDK."""

    name: str
    supports_streaming: bool

    async def synthesize(self, text: str, *, voice: str | None = None) -> SynthesizedAudio: ...

    def synthesize_stream(self, text: str) -> AsyncIterator[AudioChunk]: ...
