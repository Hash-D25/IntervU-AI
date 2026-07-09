# 17 - Realtime Voice V2: Iteration 0 (Foundations, Config & Provider Contracts)

## Goal

Lay the provider-agnostic foundations for the realtime voice-to-voice interview
(see [`16-realtime-voice-v2.md`](./16-realtime-voice-v2.md)) **without any
user-visible behavior change**: a text-to-speech contract, a live-audio streaming
extension to the speech-to-text contract, configuration + feature flag, and DI
wiring. Everything defaults to fake/off so dev and tests never hit a paid provider.

## Scope

**In:** `SpeechSynthesizer` protocol + `SynthesizedAudio`/`AudioChunk`, default
`FakeSynthesizer` strategy, synthesizer factory + DI alias, `Transcriber`
extension `transcribe_realtime(...)` with a `FakeTranscriber` implementation and a
`WhisperTranscriber` stub, new config (synthesizer/TTS/WS/turn-taking) + feature
flag, `.env.example` docs, unit tests.

**Out:** any route, WebSocket, or frontend change; real TTS providers; real
streaming STT decoding; turn-taking / VAD logic. Those arrive in iterations 1–10.

---

## Architecture

The new `ai/synthesis/` package mirrors `ai/transcription/` exactly: a protocol in
`base.py`, a config-driven `factory.py`, and swappable `strategies/`. Interview
logic depends only on the protocols, never on a concrete SDK.

```
                        (wired for later iterations - no consumer yet)
Settings ──► create_synthesizer() ──► SpeechSynthesizer ──► SynthesizedAudio / AudioChunk
   │                                        ▲
   │                                   FakeSynthesizer (default: silent WAV)
   │
   └──────► create_transcriber() ──► Transcriber
                                          ├─ transcribe()            (batch, existing)
                                          ├─ transcribe_stream()     (file → chunks, existing)
                                          └─ transcribe_realtime()   (live byte stream → chunks, NEW)
```

| Layer | Responsibility |
|-------|----------------|
| `ai/synthesis/base.py` | `SpeechSynthesizer` protocol + audio payload types |
| `ai/synthesis/factory.py` | Select synthesizer from `Settings` |
| `ai/synthesis/strategies/` | Swappable TTS engines (only `fake` today) |
| `ai/transcription/base.py` | `Transcriber` protocol, now with `transcribe_realtime` |
| `core/config.py` | Typed settings for TTS / WS / turn-taking |
| `core/container.py` | `SpeechSynthesizerDep` DI alias |

### Contracts

`SpeechSynthesizer` (mirrors the `Transcriber` shape — `name`,
`supports_streaming`, one batch + one streaming method):

```python
async def synthesize(self, text: str, *, voice: str | None = None) -> SynthesizedAudio
def synthesize_stream(self, text: str) -> AsyncIterator[AudioChunk]
```

- `SynthesizedAudio` — frozen dataclass: `content: bytes`, `content_type: str`,
  `sample_rate: int`.
- `AudioChunk` — same fields plus `is_final: bool`. **Concatenating every chunk's
  `content` in order reproduces the full payload** (documented contract).

`Transcriber` gains a live-stream method so a WebSocket can feed mic audio
incrementally instead of uploading one blob:

```python
def transcribe_realtime(self, chunks: AsyncIterator[bytes]) -> AsyncIterator[TranscriptionChunk]
```

### Strategy status

| Strategy | `transcribe_realtime` / `synthesize` | Notes |
|----------|--------------------------------------|-------|
| `FakeTranscriber` | drains the byte stream, yields scripted partial + final chunks | default for dev/tests |
| `WhisperTranscriber` | stub: raises `BadRequestError` on iteration | real chunked decoding lands in iteration 4 |
| `FakeSynthesizer` | returns a 300 ms mono 16-bit silent WAV @ 24 kHz | default for dev/tests |

> **Known contract gotcha (fix in iteration 4):** `transcribe_realtime` is an async
> generator, so the Whisper stub's `BadRequestError` only surfaces when the caller
> *starts iterating*, not when the method is called. When a live consumer exists,
> add a `supports_realtime` capability flag (parallel to `supports_streaming`) so
> callers can branch before iterating.

---

## Config

Added to `core/config.py` (env names shown) and documented in `backend/.env.example`.
All default to fake/off — no behavior change.

```env
# Feature flag - gates the entire V2 live interview. Keep false until wired up.
REALTIME_INTERVIEW_ENABLED=false

# Text-to-speech engine.
# fake = silent placeholder (dev/tests); browser = client-side SpeechSynthesis;
# groq | openai | gemini | elevenlabs = paid providers (added in later iterations).
SYNTHESIZER=fake
TTS_VOICE=
TTS_MODEL=
TTS_API_KEY=
TTS_BASE_URL=

# WebSocket session guardrails + turn-taking thresholds (consumed in iterations 3-5).
WS_MAX_SESSION_MINUTES=30
TURN_SILENCE_MS=1500      # silence after speech that ends a turn
TURN_MIN_SPEECH_MS=800    # minimum speech before a turn can end
```

| Setting | Default | Consumed by |
|---------|---------|-------------|
| `realtime_interview_enabled` | `False` | WS endpoint gate (iter 3) |
| `synthesizer` | `fake` | `create_synthesizer` (iter 0) / TTS route (iter 1) |
| `tts_voice` / `tts_model` / `tts_api_key` / `tts_base_url` | `""` | real TTS providers (iter 1) |
| `ws_max_session_minutes` | `30` | `LiveSession` lifetime (iter 3) |
| `turn_silence_ms` | `1500` | end-of-utterance detection (iter 5) |
| `turn_min_speech_ms` | `800` | end-of-utterance detection (iter 5) |

---

## Dependency injection

The synthesizer factory is exposed through the DI container like the other
providers. No route consumes it yet; it is scaffolding for iteration 1.

```python
# core/container.py
def get_synthesizer(settings: SettingsDep) -> SpeechSynthesizer:
    return create_synthesizer(settings)

SpeechSynthesizerDep = Annotated[SpeechSynthesizer, Depends(get_synthesizer)]
```

> When iteration 1 adds `features/speech/`, move this DI into
> `features/speech/dependencies.py` to match how `create_transcriber` is wired in
> `features/voice/dependencies.py`.

---

## Files

| Path | Change |
|------|--------|
| `backend/app/ai/synthesis/base.py` | new - protocol + `SynthesizedAudio`/`AudioChunk` |
| `backend/app/ai/synthesis/factory.py` | new - `create_synthesizer(settings)` |
| `backend/app/ai/synthesis/strategies/__init__.py` | new - package marker |
| `backend/app/ai/synthesis/strategies/fake_synthesizer.py` | new - `FakeSynthesizer` |
| `backend/app/ai/synthesis/README.md` | new - module overview |
| `backend/app/ai/transcription/base.py` | + `transcribe_realtime` on protocol |
| `backend/app/ai/transcription/strategies/fake_transcriber.py` | + `transcribe_realtime`; dedup scripted chunks |
| `backend/app/ai/transcription/strategies/whisper_transcriber.py` | + `transcribe_realtime` stub |
| `backend/app/core/config.py` | + synthesizer / TTS / WS / turn-taking settings |
| `backend/app/core/container.py` | + `get_synthesizer` + `SpeechSynthesizerDep` |
| `backend/.env.example` | + "Realtime voice-to-voice interview (V2)" section |
| `backend/tests/unit/test_synthesizer.py` | new - factory + `FakeSynthesizer` |
| `backend/tests/unit/test_transcriber_realtime.py` | new - realtime contract + Whisper conformance |

---

## Testing

| Test | Verifies |
|------|----------|
| `test_factory_returns_fake_synthesizer_by_default` | factory default is `FakeSynthesizer` |
| `test_factory_rejects_unknown_synthesizer` | unknown value → `BadRequestError` |
| `test_synthesize_returns_wav_payload` | valid WAV bytes, `audio/wav`, 24 kHz |
| `test_synthesize_stream_yields_reassemblable_chunks` | chunks reassemble to full payload; last is final |
| `test_fake_transcriber_realtime_yields_partial_then_final` | live stream → partial + final chunks |
| `test_fake_transcriber_realtime_handles_empty_stream` | empty byte stream still yields a final chunk |
| `test_whisper_satisfies_extended_transcriber_protocol` | `WhisperTranscriber` still structurally matches `Transcriber` |
| `test_whisper_realtime_stub_raises_on_iteration` | stub raises `BadRequestError` when iterated |

---

## Verification

```bash
cd backend
ruff check .
mypy app
pytest tests/unit/test_synthesizer.py tests/unit/test_transcriber_realtime.py -q
```

**Acceptance (met):** factory returns `FakeSynthesizer` by default; the extended
contracts compile (`mypy app` clean); new tests green; no route/frontend change.

> Pre-existing `ruff`/`mypy` findings in unrelated files (e.g. `core/security/google.py`,
> `shared/llm_json.py`, `app/main.py`, some migrations/tests) are untouched by this
> iteration.

## What's next

**Iteration 1 — Text-to-Speech layer:** add `features/speech/` (service, schemas,
router, dependencies), a `POST /api/v1/speech/synthesize` endpoint, one real TTS
provider behind `SpeechSynthesizer`, and a frontend `useInterviewerVoice` hook with
a browser `SpeechSynthesis` fallback.
