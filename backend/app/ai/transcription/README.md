# ai/transcription

Speech-to-text engines behind a stable interface.

- `base.py` — `Transcriber` protocol + `ProcessedAudio`
- `schemas.py` — `TranscriptionResult`, `TranscriptionChunk` (batch + streaming)
- `factory.py` — `create_transcriber(settings)`
- `strategies/whisper_transcriber.py` — faster-whisper implementation
- `strategies/fake_transcriber.py` — deterministic test/dev transcriber

Interview execution consumes **text transcripts only**. The voice feature
transcribes audio and returns text; callers submit that text to the existing
execution answer endpoint.
