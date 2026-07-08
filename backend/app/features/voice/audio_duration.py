"""Best-effort audio duration detection for upload validation."""

import io
import wave


def estimate_audio_duration_seconds(content: bytes, content_type: str) -> float | None:
    normalized = content_type.split(";", 1)[0].strip().lower()
    if normalized in {"audio/wav", "audio/x-wav"}:
        return _wav_duration_seconds(content)
    return None


def _wav_duration_seconds(content: bytes) -> float | None:
    try:
        with wave.open(io.BytesIO(content), "rb") as handle:
            frame_rate = handle.getframerate()
            frame_count = handle.getnframes()
            if frame_rate <= 0:
                return None
            return frame_count / frame_rate
    except (wave.Error, EOFError):
        return None
