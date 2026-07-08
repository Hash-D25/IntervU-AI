"""Voice transcription API routes."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, File, Query, UploadFile, status
from fastapi.responses import StreamingResponse

from app.features.auth.dependencies import CurrentUserDep
from app.features.voice.dependencies import (
    AudioProcessorDep,
    TranscriptionContextLoaderDep,
    VoiceTranscriptionServiceDep,
)
from app.features.voice.schemas import TranscribeResponse
from app.features.voice.transcribe_stream import stream_transcription_events

router = APIRouter(prefix="/voice", tags=["voice"])


@router.post("/transcribe", response_model=TranscribeResponse, status_code=status.HTTP_200_OK)
async def transcribe_audio(
    current_user: CurrentUserDep,
    service: VoiceTranscriptionServiceDep,
    audio_processor: AudioProcessorDep,
    context_loader: TranscriptionContextLoaderDep,
    file: Annotated[UploadFile, File()],
    interview_id: Annotated[UUID | None, Query()] = None,
) -> TranscribeResponse:
    audio = await audio_processor.process_upload(file)
    context = await context_loader.load(user_id=current_user.id, interview_id=interview_id)
    return await service.transcribe(audio, context=context)


@router.post("/transcribe/stream")
async def transcribe_audio_stream(
    current_user: CurrentUserDep,
    service: VoiceTranscriptionServiceDep,
    audio_processor: AudioProcessorDep,
    context_loader: TranscriptionContextLoaderDep,
    file: Annotated[UploadFile, File()],
    interview_id: Annotated[UUID | None, Query()] = None,
) -> StreamingResponse:
    audio = await audio_processor.process_upload(file)
    context = await context_loader.load(user_id=current_user.id, interview_id=interview_id)
    return StreamingResponse(
        stream_transcription_events(service, audio, context=context),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
