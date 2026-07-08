"""Speech-to-text orchestration.

Converts uploaded audio into transcripts. Interview submission remains a
separate step so audio processing never couples to execution state machines.
"""

from collections.abc import AsyncIterator

from app.ai.transcription.base import ProcessedAudio, Transcriber
from app.ai.transcription.schemas import TranscriptionChunk, TranscriptionResult
from app.features.voice.protocols import TranscriptRefiner
from app.features.voice.schemas import TranscribeResponse, TranscriptionContext


class VoiceTranscriptionService:
    def __init__(
        self,
        transcriber: Transcriber,
        refiner: TranscriptRefiner,
    ) -> None:
        self._transcriber = transcriber
        self._refiner = refiner

    @property
    def supports_streaming(self) -> bool:
        return self._transcriber.supports_streaming

    @property
    def transcriber_name(self) -> str:
        return self._transcriber.name

    async def transcribe(
        self,
        audio: ProcessedAudio,
        *,
        context: TranscriptionContext | None = None,
    ) -> TranscribeResponse:
        active_context = context or TranscriptionContext()
        prepared_audio = _with_prompt(audio, active_context.initial_prompt)
        result = await self._transcriber.transcribe(prepared_audio)
        refined = await self._maybe_refine(result, active_context)
        return refined

    async def finalize_transcript(
        self,
        transcript: str,
        *,
        context: TranscriptionContext | None = None,
    ) -> TranscribeResponse:
        active_context = context or TranscriptionContext()
        result = TranscriptionResult(
            transcript=transcript,
            transcriber_name=self._transcriber.name,
            is_final=True,
        )
        return await self._maybe_refine(result, active_context)

    async def transcribe_stream(
        self,
        audio: ProcessedAudio,
        *,
        context: TranscriptionContext | None = None,
    ) -> AsyncIterator[TranscriptionChunk]:
        active_context = context or TranscriptionContext()
        prepared_audio = _with_prompt(audio, active_context.initial_prompt)
        async for chunk in self._transcriber.transcribe_stream(prepared_audio):
            yield chunk

    async def _maybe_refine(
        self,
        result: TranscriptionResult,
        context: TranscriptionContext,
    ) -> TranscribeResponse:
        transcript = result.transcript
        refined = False
        if self._refiner.name != "none":
            transcript = await self._refiner.refine(transcript, context=context)
            refined = transcript != result.transcript
        return _to_response(result, transcript=transcript, refined=refined)


def _with_prompt(audio: ProcessedAudio, initial_prompt: str) -> ProcessedAudio:
    prompt = initial_prompt.strip() or None
    if audio.initial_prompt == prompt:
        return audio
    return ProcessedAudio(
        content=audio.content,
        content_type=audio.content_type,
        filename=audio.filename,
        initial_prompt=prompt,
    )


def _to_response(
    result: TranscriptionResult,
    *,
    transcript: str,
    refined: bool,
) -> TranscribeResponse:
    return TranscribeResponse(
        transcript=transcript,
        language=result.language,
        duration_ms=result.duration_ms,
        transcriber_name=result.transcriber_name,
        chunks=result.chunks,
        words=result.words,
        refined=refined,
    )
