# ai/providers

Provider-agnostic LLM access.

- `base.py` — `LLMProvider` protocol/interface (the contract services depend on).
- `openai_compatible.py` — implementation for any OpenAI-compatible endpoint.

Add a new provider by adding a file that satisfies the interface. No service or
feature code changes when swapping providers.
