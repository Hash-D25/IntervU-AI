# 12 - Voice Pipeline

## Goal

Add microphone capture, speech-to-text, and transcript generation while keeping
audio processing separate from interview execution logic.

## Scope

**In:** `Transcriber` protocol, Whisper + fake strategies, voice feature
(audio validation + transcription service), batch + SSE streaming endpoints,
frontend microphone recorder, interview page that transcribes then submits text.

**Out:** text-to-speech for interviewer voice, WebSocket live streaming, auto-submit
without user transcript review.

---

## Architecture

```
Browser microphone (MediaRecorder)
        │
        ▼
POST /voice/transcribe  (or /voice/transcribe/stream)
        │
        ▼
AudioProcessor → VoiceTranscriptionService → Transcriber
        │
        ▼
TranscribeResponse { transcript }
        │
        ▼  (separate step - interview logic unchanged)
POST /interviews/{id}/execution/answer { transcript }
```

| Layer | Responsibility |
|-------|----------------|
| `features/voice/audio_processor.py` | Upload validation, `ProcessedAudio` |
| `features/voice/service.py` | Orchestrate transcription only |
| `ai/transcription/` | Swappable STT engines |
| `interview/execution/` | Text answers only (unchanged) |

### Streaming-ready design

- `TranscriptionChunk` - partial/final text slices with optional timestamps
- `Transcriber.transcribe_stream()` - async chunk iterator
- `POST /voice/transcribe/stream` - SSE events (`started`, `chunk`, `done`, `error`)

Whisper currently yields segment-level chunks; true realtime streaming can plug
into the same contract later.

---

## Config

```env
TRANSCRIBER=fake          # dev/tests
TRANSCRIBER=whisper       # production (pip install -e ".[voice]")
WHISPER_MODEL=base        # tiny | base | small | medium | large-v3
VOICE_MAX_SIZE_MB=25
WHISPER_LANGUAGE=         # empty = auto-detect
WHISPER_DEVICE=cpu        # cpu | cuda
WHISPER_COMPUTE_TYPE=int8
ENABLE_VAD=true
MAX_AUDIO_DURATION_SECONDS=300
SUPPORTED_AUDIO_FORMATS=wav,mp3,m4a,webm,ogg
RETURN_WORD_TIMESTAMPS=false
```

---

## API

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/voice/transcribe` | Upload audio → transcript JSON |
| POST | `/api/v1/voice/transcribe/stream` | Upload audio → SSE chunk stream |

Supported uploads: `webm`, `wav`, `mp3`, `m4a`, `ogg`.

---

## Frontend

| Path | Purpose |
|------|---------|
| `features/voice/hooks/useMicrophone.ts` | `getUserMedia` + `MediaRecorder` |
| `features/voice/components/MicrophoneRecorder.tsx` | Record → transcribe |
| `features/interview/components/VoiceAnswerPanel.tsx` | Transcript review + submit |
| `app/interviews/[id]/page.tsx` | Voice interview session page |

Flow: **record → transcribe → edit transcript → submit answer**.

---

## Verification

```bash
cd backend
ruff check .
mypy app
pytest tests/unit/test_audio_processor.py tests/unit/test_voice_service.py tests/integration/test_voice_transcription.py -q

cd ../frontend
npm run typecheck
```

## What's next

Realtime streaming from the microphone, interviewer TTS, and richer interview UI.
