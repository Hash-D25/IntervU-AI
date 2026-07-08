"""Server-sent events stream for incremental transcription."""

import json
from collections.abc import AsyncIterator

from app.ai.transcription.base import ProcessedAudio
from app.core.exceptions import AppError
from app.features.voice.schemas import TranscriptionContext, TranscriptionStreamEvent
from app.features.voice.service import VoiceTranscriptionService


async def stream_transcription_events(
    service: VoiceTranscriptionService,
    audio: ProcessedAudio,
    *,
    context: TranscriptionContext | None = None,
) -> AsyncIterator[str]:
    if not service.supports_streaming:
        yield _format_event(
            TranscriptionStreamEvent(
                stage="error",
                message="Configured transcriber does not support streaming",
            )
        )
        return

    transcript_parts: list[str] = []
    try:
        yield _format_event(
            TranscriptionStreamEvent(
                stage="started",
                message="Transcription started",
            )
        )
        async for chunk in service.transcribe_stream(audio, context=context):
            transcript_parts.append(chunk.text)
            yield _format_event(
                TranscriptionStreamEvent(
                    stage="chunk",
                    message="Partial transcript",
                    chunk=chunk,
                )
            )
        transcript = "".join(transcript_parts).strip()
        if not transcript:
            raise AppError("No speech detected in audio", status_code=422)
        result = await service.finalize_transcript(transcript, context=context)
        yield _format_event(
            TranscriptionStreamEvent(
                stage="done",
                message="Transcription complete",
                result=result,
            )
        )
    except AppError as exc:
        yield _format_event(
            TranscriptionStreamEvent(stage="error", message=exc.message)
        )
    except Exception as exc:
        yield _format_event(
            TranscriptionStreamEvent(stage="error", message=str(exc))
        )


def _format_event(event: TranscriptionStreamEvent) -> str:
    return f"data: {json.dumps(event.model_dump(mode='json'))}\n\n"
