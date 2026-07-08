# features/voice

Audio processing and speech-to-text. **Does not** submit interview answers.

Responsibility: accept microphone recordings, validate audio, transcribe to text.

- `audio_processor.py` — upload validation + `ProcessedAudio`
- `service.py` — `VoiceTranscriptionService` (delegates to `Transcriber`)
- `transcribe_stream.py` — SSE chunk stream (streaming-ready contract)
- Transcription engines live in `app/ai/transcription/`

Interview clients should:

1. `POST /voice/transcribe` (or `/voice/transcribe/stream`) → transcript
2. `POST /interviews/{id}/execution/answer` with `{ "transcript": "..." }`
