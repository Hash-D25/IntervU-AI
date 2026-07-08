"""Transcription result models shared by batch and streaming paths."""

from pydantic import BaseModel, Field


class TranscriptionChunk(BaseModel):
    """A partial or final slice of transcribed speech.

    Streaming implementations yield incremental chunks; batch implementations
    typically return a single final chunk.
    """

    text: str = Field(min_length=1)
    is_final: bool = False
    start_ms: int | None = Field(default=None, ge=0)
    end_ms: int | None = Field(default=None, ge=0)


class TranscriptionWord(BaseModel):
    text: str = Field(min_length=1)
    start_ms: int = Field(ge=0)
    end_ms: int = Field(ge=0)


class TranscriptionResult(BaseModel):
    transcript: str = Field(min_length=1, max_length=20_000)
    language: str | None = Field(default=None, max_length=16)
    duration_ms: int | None = Field(default=None, ge=0)
    confidence: float | None = Field(default=None, ge=0, le=1)
    chunks: list[TranscriptionChunk] = Field(default_factory=list)
    words: list[TranscriptionWord] = Field(default_factory=list)
    transcriber_name: str = Field(min_length=1, max_length=64)
    is_final: bool = True
