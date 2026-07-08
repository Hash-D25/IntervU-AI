"""Voice feature dependency wiring."""

from typing import Annotated

from fastapi import Depends

from app.ai.transcription.factory import create_transcriber
from app.core.container import SessionDep, SettingsDep
from app.features.voice.audio_formats import parse_supported_audio_formats
from app.features.voice.audio_processor import AudioProcessor
from app.features.voice.context_loader import (
    TranscriptionContextLoader,
    create_transcription_context_loader,
)
from app.features.voice.factory import create_transcript_refiner
from app.features.voice.service import VoiceTranscriptionService


def get_audio_processor(settings: SettingsDep) -> AudioProcessor:
    return AudioProcessor(
        max_bytes=settings.voice_max_size_mb * 1024 * 1024,
        max_duration_seconds=settings.max_audio_duration_seconds,
        supported_content_types=parse_supported_audio_formats(
            settings.supported_audio_formats
        ),
    )


def get_voice_transcription_service(settings: SettingsDep) -> VoiceTranscriptionService:
    return VoiceTranscriptionService(
        create_transcriber(settings),
        create_transcript_refiner(settings),
    )


def get_transcription_context_loader(session: SessionDep) -> TranscriptionContextLoader:
    return create_transcription_context_loader(session)


VoiceTranscriptionServiceDep = Annotated[
    VoiceTranscriptionService,
    Depends(get_voice_transcription_service),
]
AudioProcessorDep = Annotated[AudioProcessor, Depends(get_audio_processor)]
TranscriptionContextLoaderDep = Annotated[
    TranscriptionContextLoader,
    Depends(get_transcription_context_loader),
]
