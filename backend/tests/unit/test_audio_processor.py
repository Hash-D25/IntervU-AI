"""Audio processor unit tests."""

import struct
import wave
from io import BytesIO

import pytest
from fastapi import UploadFile

from app.core.exceptions import BadRequestError, PayloadTooLargeError
from app.features.voice.audio_formats import parse_supported_audio_formats
from app.features.voice.audio_processor import AudioProcessor


def _upload(
    content: bytes,
    *,
    content_type: str = "audio/webm",
    filename: str = "answer.webm",
) -> UploadFile:
    return UploadFile(
        file=BytesIO(content),
        filename=filename,
        headers={"content-type": content_type},
    )


def _processor(**kwargs: object) -> AudioProcessor:
    defaults = {
        "max_bytes": 1024 * 1024,
        "max_duration_seconds": 300,
        "supported_content_types": parse_supported_audio_formats("wav,mp3,m4a,webm"),
    }
    defaults.update(kwargs)
    return AudioProcessor(**defaults)  # type: ignore[arg-type]


def _wav_bytes(duration_seconds: float = 1.0) -> bytes:
    buffer = BytesIO()
    with wave.open(buffer, "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(8000)
        frame_count = int(8000 * duration_seconds)
        handle.writeframes(struct.pack("<h", 0) * frame_count)
    return buffer.getvalue()


@pytest.mark.asyncio
async def test_process_upload_accepts_webm_audio() -> None:
    processor = _processor()
    audio = await processor.process_upload(_upload(b"x" * 512))
    assert audio.content_type == "audio/webm"
    assert len(audio.content) == 512


@pytest.mark.asyncio
async def test_process_upload_accepts_m4a_with_generic_content_type() -> None:
    processor = _processor()
    audio = await processor.process_upload(
        _upload(b"x" * 512, content_type="application/octet-stream", filename="note.m4a")
    )
    assert audio.content_type == "audio/mp4"


@pytest.mark.asyncio
async def test_process_upload_rejects_unsupported_type() -> None:
    processor = _processor()
    with pytest.raises(BadRequestError):
        await processor.process_upload(_upload(b"x" * 512, content_type="application/pdf"))


@pytest.mark.asyncio
async def test_process_upload_rejects_oversized_audio() -> None:
    processor = _processor(max_bytes=400)
    with pytest.raises(PayloadTooLargeError):
        await processor.process_upload(_upload(b"x" * 512))


@pytest.mark.asyncio
async def test_process_upload_rejects_long_wav_audio() -> None:
    processor = _processor(max_duration_seconds=1)
    with pytest.raises(BadRequestError, match="maximum duration"):
        await processor.process_upload(
            _upload(_wav_bytes(duration_seconds=2.0), content_type="audio/wav", filename="a.wav")
        )
