"""Voice feature API schemas."""

from pydantic import BaseModel, Field

from app.ai.transcription.schemas import TranscriptionChunk, TranscriptionWord


class TranscriptionContext(BaseModel):
    initial_prompt: str = ""
    hint_terms: list[str] = Field(default_factory=list)
    company_name: str | None = None
    target_role: str | None = None


class TranscribeResponse(BaseModel):
    transcript: str = Field(min_length=1, max_length=20_000)
    language: str | None = Field(default=None, max_length=16)
    duration_ms: int | None = Field(default=None, ge=0)
    transcriber_name: str = Field(min_length=1, max_length=64)
    chunks: list[TranscriptionChunk] = Field(default_factory=list)
    words: list[TranscriptionWord] = Field(default_factory=list)
    refined: bool = False


class TranscriptionStreamEvent(BaseModel):
    stage: str = Field(min_length=1, max_length=32)
    message: str = Field(min_length=1, max_length=500)
    chunk: TranscriptionChunk | None = None
    result: TranscribeResponse | None = None
