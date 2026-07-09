# ai/synthesis

Text-to-speech engines behind a stable interface (V2 realtime voice).

- `base.py` - `SpeechSynthesizer` protocol + `SynthesizedAudio` / `AudioChunk`
- `factory.py` - `create_synthesizer(settings)`
- `strategies/fake_synthesizer.py` - deterministic test/dev synthesizer (silent WAV)

The interviewer speaks synthesized question audio; interview logic never depends
on a concrete TTS SDK. `FakeSynthesizer` is the default so dev/tests never call a
paid provider. Real providers (Groq PlayAI, OpenAI, Gemini, ElevenLabs) are added
behind this protocol in later iterations.
