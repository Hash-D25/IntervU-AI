# app/ai

The **AI boundary**. Everything model-specific is isolated here so providers are
swappable and business logic never depends on a concrete vendor.

```
ai/
├── providers/       # LLMProvider interface + implementations (OpenAI-compatible)
├── prompts/         # prompt templates stored as data, not inline in logic
├── graphs/          # LangGraph state machines (explicit interview flow)
├── vectorstore/     # ChromaDB wrapper for resume/JD retrieval
└── transcription/   # Whisper wrapper behind an interface
```

Rules:

- Business logic depends on **interfaces** defined here, never on SDK types.
- Prompts are versioned data files, edited without touching code.
- Swapping a provider means adding one implementation, not editing services.
