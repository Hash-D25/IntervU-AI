"""Audio format parsing tests."""

import pytest

from app.core.exceptions import BadRequestError
from app.features.voice.audio_formats import (
    parse_supported_audio_formats,
    resolve_upload_content_type,
    supported_format_labels,
)


def test_parse_supported_audio_formats_maps_extensions() -> None:
    content_types = parse_supported_audio_formats("wav,mp3,m4a,webm")
    assert "audio/webm" in content_types
    assert "audio/mpeg" in content_types
    assert "audio/mp4" in content_types
    assert "audio/ogg" not in content_types


def test_supported_format_labels_lists_configured_formats() -> None:
    content_types = parse_supported_audio_formats("wav,webm")
    assert supported_format_labels(content_types) == "wav, webm"


def test_resolve_m4a_from_x_m4a_content_type() -> None:
    supported = parse_supported_audio_formats("wav,mp3,m4a,webm")
    resolved = resolve_upload_content_type(
        "audio/x-m4a",
        "answer.m4a",
        supported_content_types=supported,
    )
    assert resolved == "audio/mp4"


def test_resolve_m4a_from_octet_stream_and_filename() -> None:
    supported = parse_supported_audio_formats("wav,mp3,m4a,webm")
    resolved = resolve_upload_content_type(
        "application/octet-stream",
        "recording.m4a",
        supported_content_types=supported,
    )
    assert resolved == "audio/mp4"


def test_resolve_m4a_from_video_mp4_when_filename_is_m4a() -> None:
    supported = parse_supported_audio_formats("wav,mp3,m4a,webm")
    resolved = resolve_upload_content_type(
        "video/mp4",
        "voice-note.m4a",
        supported_content_types=supported,
    )
    assert resolved == "audio/mp4"


def test_rejects_video_mp4_without_m4a_extension() -> None:
    supported = parse_supported_audio_formats("wav,mp3,m4a,webm")
    with pytest.raises(BadRequestError):
        resolve_upload_content_type(
            "video/mp4",
            "clip.mp4",
            supported_content_types=supported,
        )
