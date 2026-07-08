"""faster-whisper transcription strategy."""

import asyncio
import tempfile
from collections.abc import AsyncIterator
from dataclasses import dataclass
from pathlib import Path

from app.ai.transcription.base import ProcessedAudio
from app.ai.transcription.schemas import (
    TranscriptionChunk,
    TranscriptionResult,
    TranscriptionWord,
)
from app.core.config import Settings
from app.core.exceptions import BadRequestError, ParseError

_CONTENT_TYPE_SUFFIX = {
    "audio/webm": ".webm",
    "video/webm": ".webm",
    "audio/wav": ".wav",
    "audio/x-wav": ".wav",
    "audio/mpeg": ".mp3",
    "audio/mp3": ".mp3",
    "audio/x-mpeg": ".mp3",
    "audio/mp4": ".m4a",
    "audio/x-m4a": ".m4a",
    "audio/m4a": ".m4a",
    "audio/mp4a-latm": ".m4a",
    "video/mp4": ".m4a",
    "audio/ogg": ".ogg",
    "application/ogg": ".ogg",
}


@dataclass(frozen=True, slots=True)
class _SegmentPayload:
    text: str
    start_ms: int
    end_ms: int
    words: list[TranscriptionWord]


class WhisperTranscriber:
    name = "whisper"
    supports_streaming = True

    def __init__(
        self,
        *,
        model_name: str,
        language: str | None,
        device: str,
        compute_type: str,
        enable_vad: bool,
        return_word_timestamps: bool,
        beam_size: int,
    ) -> None:
        self._model_name = model_name
        self._language = language
        self._device = device
        self._compute_type = compute_type
        self._enable_vad = enable_vad
        self._return_word_timestamps = return_word_timestamps
        self._beam_size = beam_size
        self._model: object | None = None

    async def transcribe(self, audio: ProcessedAudio) -> TranscriptionResult:
        suffix = _suffix_for_content_type(audio.content_type)
        segments, language, duration_ms, words = await asyncio.to_thread(
            self._transcribe_payload,
            audio.content,
            suffix,
            audio.initial_prompt,
        )
        if not segments:
            raise ParseError("No speech detected in audio")
        transcript = "".join(segment.text for segment in segments).strip()
        chunks = [
            TranscriptionChunk(
                text=segment.text,
                is_final=index == len(segments) - 1,
                start_ms=segment.start_ms,
                end_ms=segment.end_ms,
            )
            for index, segment in enumerate(segments)
        ]
        return TranscriptionResult(
            transcript=transcript,
            language=language,
            duration_ms=duration_ms,
            chunks=chunks,
            words=words,
            transcriber_name=self.name,
            is_final=True,
        )

    async def transcribe_stream(
        self,
        audio: ProcessedAudio,
    ) -> AsyncIterator[TranscriptionChunk]:
        suffix = _suffix_for_content_type(audio.content_type)
        segments, _language, _duration_ms, _words = await asyncio.to_thread(
            self._transcribe_payload,
            audio.content,
            suffix,
            audio.initial_prompt,
        )
        if not segments:
            raise ParseError("No speech detected in audio")
        for index, segment in enumerate(segments):
            yield TranscriptionChunk(
                text=segment.text,
                is_final=index == len(segments) - 1,
                start_ms=segment.start_ms,
                end_ms=segment.end_ms,
            )

    def _transcribe_payload(
        self,
        content: bytes,
        suffix: str,
        initial_prompt: str | None,
    ) -> tuple[list[_SegmentPayload], str | None, int | None, list[TranscriptionWord]]:
        model = self._load_model()
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as handle:
            handle.write(content)
            temp_path = Path(handle.name)
        try:
            transcribe_kwargs: dict[str, object] = {
                "language": self._language,
                "vad_filter": self._enable_vad,
                "word_timestamps": self._return_word_timestamps,
                "beam_size": self._beam_size,
            }
            if initial_prompt:
                transcribe_kwargs["initial_prompt"] = initial_prompt
            segments, info = model.transcribe(  # type: ignore[attr-defined]
                str(temp_path),
                **transcribe_kwargs,
            )
            parsed_segments: list[_SegmentPayload] = []
            words: list[TranscriptionWord] = []
            for segment in segments:
                text = segment.text.strip()
                if not text:
                    continue
                segment_words = _extract_words(segment)
                words.extend(segment_words)
                parsed_segments.append(
                    _SegmentPayload(
                        text=text if text.endswith(" ") else f"{text} ",
                        start_ms=int(segment.start * 1000),
                        end_ms=int(segment.end * 1000),
                        words=segment_words,
                    )
                )
            duration_ms = None
            if info.duration:
                duration_ms = int(info.duration * 1000)
            language = info.language or self._language
            return parsed_segments, language, duration_ms, words
        finally:
            temp_path.unlink(missing_ok=True)

    def _load_model(self) -> object:
        if self._model is not None:
            return self._model
        try:
            from faster_whisper import WhisperModel
        except ImportError as exc:
            raise BadRequestError(
                'Whisper transcription requires the voice optional dependency. '
                'Install with: pip install -e ".[voice]"'
            ) from exc
        self._model = WhisperModel(
            self._model_name,
            device=self._device,
            compute_type=self._compute_type,
        )
        return self._model


def create_whisper_transcriber(settings: Settings) -> WhisperTranscriber:
    language = settings.whisper_language.strip() or None
    return WhisperTranscriber(
        model_name=settings.whisper_model,
        language=language,
        device=settings.whisper_device,
        compute_type=settings.whisper_compute_type,
        enable_vad=settings.enable_vad,
        return_word_timestamps=settings.return_word_timestamps,
        beam_size=settings.whisper_beam_size,
    )


def _extract_words(segment: object) -> list[TranscriptionWord]:
    raw_words = getattr(segment, "words", None)
    if not raw_words:
        return []
    parsed: list[TranscriptionWord] = []
    for word in raw_words:
        text = getattr(word, "word", "").strip()
        if not text:
            continue
        parsed.append(
            TranscriptionWord(
                text=text,
                start_ms=int(getattr(word, "start", 0.0) * 1000),
                end_ms=int(getattr(word, "end", 0.0) * 1000),
            )
        )
    return parsed


def _suffix_for_content_type(content_type: str) -> str:
    normalized = content_type.split(";", 1)[0].strip().lower()
    suffix = _CONTENT_TYPE_SUFFIX.get(normalized)
    if suffix is None:
        raise BadRequestError(f"Unsupported audio content type: {content_type}")
    return suffix
