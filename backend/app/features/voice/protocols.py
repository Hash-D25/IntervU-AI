"""Optional post-STT transcript cleanup."""

from typing import Protocol, runtime_checkable

from app.features.voice.schemas import TranscriptionContext


@runtime_checkable
class TranscriptRefiner(Protocol):
    name: str

    async def refine(self, transcript: str, *, context: TranscriptionContext) -> str: ...
