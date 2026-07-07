# ai/providers

Provider-agnostic LLM access.

- `base.py` — `LLMProvider` protocol (the contract services depend on).
- `factory.py` — `create_llm_provider(settings)` maps `LLM_PROVIDER` to an impl.
- `openai_compatible.py` — OpenAI, Groq, and Ollama (OpenAI-compatible APIs).
- `gemini.py` — Google Gemini REST provider.

Add a new provider by adding a file that satisfies the interface and registering
it in `factory.py`. No service or feature code changes when swapping providers.

Supported values for `LLM_PROVIDER`:

| Value | Backend | JSON mode |
| ----- | ------- | --------- |
| `ollama` | Local Ollama | prompt-only |
| `groq` | Groq cloud | native |
| `openai` | OpenAI | native |
| `gemini` | Google Gemini | native (`responseMimeType`) |
