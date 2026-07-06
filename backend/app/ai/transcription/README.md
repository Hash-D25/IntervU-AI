# ai/transcription

Speech-to-text for voice interviews.

- `base.py` — `Transcriber` interface.
- `whisper.py` — Whisper-based implementation.

Business logic depends on the interface, so the transcription engine can change
without touching the voice feature.
