"""Audio upload validation and normalization.

This module owns audio I/O concerns only. It does not know about interviews,
questions, or execution state.
"""

from fastapi import UploadFile

from app.ai.transcription.base import ProcessedAudio
from app.core.exceptions import BadRequestError, PayloadTooLargeError
from app.features.voice.audio_duration import estimate_audio_duration_seconds
from app.features.voice.audio_formats import resolve_upload_content_type

_MIN_AUDIO_BYTES = 256


class AudioProcessor:
    def __init__(
        self,
        *,
        max_bytes: int,
        max_duration_seconds: int,
        supported_content_types: frozenset[str],
    ) -> None:
        self._max_bytes = max_bytes
        self._max_duration_seconds = max_duration_seconds
        self._supported_content_types = supported_content_types

    async def process_upload(self, upload_file: UploadFile) -> ProcessedAudio:
        content_type = resolve_upload_content_type(
            upload_file.content_type,
            upload_file.filename,
            supported_content_types=self._supported_content_types,
        )

        content = await upload_file.read()
        if not content:
            raise BadRequestError("Audio file is empty")
        if len(content) < _MIN_AUDIO_BYTES:
            raise BadRequestError("Audio file is too short to transcribe")
        if len(content) > self._max_bytes:
            raise PayloadTooLargeError(
                f"Audio file exceeds {self._max_bytes // (1024 * 1024)} MB limit"
            )

        duration_seconds = estimate_audio_duration_seconds(content, content_type)
        if (
            duration_seconds is not None
            and duration_seconds > self._max_duration_seconds
        ):
            raise BadRequestError(
                f"Audio exceeds maximum duration of {self._max_duration_seconds} seconds"
            )

        filename = (upload_file.filename or "recording.webm").strip()
        return ProcessedAudio(
            content=content,
            content_type=content_type,
            filename=filename,
        )
