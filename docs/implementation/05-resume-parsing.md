# 05 — Resume Parsing

## Goal

Parse an uploaded PDF resume into structured data (skills, projects, experience,
technologies, education), validate the output, and store it **separately** from
the raw file. Parsers and LLM backends are **pluggable** — swap via env vars.

## Scope

**In:** `ResumeParser` protocol, `LlmResumeParser`, **`HybridResumeParser`**
(rules + LLM gap-fill), PDF text extraction, validation layer,
`resume_parsed_profiles` table, **`create_llm_provider` factory** (Ollama /
Groq / Gemini / OpenAI), `ResumeParsingService`, `POST/GET .../parse|parsed`,
tests, migration `0004_resume_parsed_profiles`.

**Out:** auto-parse on upload, PyMuPDF swap, vector indexing.

---

## Architecture

```
POST /resumes/{id}/parse
        │
        ▼
 ResumeParsingService
        │
        ├── FileStorageService.fetch()
        ├── ResumeParser.parse()          ← hybrid (default) or llm
        ├── ParsedResumeValidator
        └── ResumeParsedProfileRepository.upsert_*()
```

### Hybrid parser (default)

```
PDF bytes
    ↓
pypdf → plain text
    ↓
RuleBasedResumeExtractor   (skills / technologies via sections + keywords)
    ↓
LLM gap-fill prompt        (only when projects / experience / education missing)
    ↓
merge_parsed()             (rules win for skills; LLM fills structure)
    ↓
ParsedResumeValidator
```

### LLM provider layer

```
LlmResumeParser / HybridResumeParser
        ↓
create_llm_provider(settings)
        ↓
┌─────────────────────────────────────────────┐
│ ollama │ groq │ openai → OpenAICompatible   │
│ gemini               → GeminiLLMProvider      │
└─────────────────────────────────────────────┘
```

| Piece | Location |
| ----- | -------- |
| Structured models | `parsing/schemas.py` |
| Parser contract | `parsing/protocols.py` |
| LLM strategy | `parsing/strategies/llm_parser.py` |
| Hybrid strategy | `parsing/strategies/hybrid_parser.py` |
| Rule extraction | `parsing/strategies/rule_extractor.py` |
| Merge helper | `parsing/strategies/merge.py` |
| Factory | `parsing/factory.py` → `RESUME_PARSER=hybrid\|llm` |
| Prompts | `resume_parsing.txt`, `resume_parsing_hybrid.txt` |
| LLM factory | `app/ai/providers/factory.py` |
| Parsed storage | `parsed_models.py` |

---

## Config

### Development (₹0 — Ollama + Qwen)

```env
RESUME_PARSER=hybrid
LLM_PROVIDER=ollama
LLM_BASE_URL=http://localhost:11434/v1
LLM_MODEL=qwen3:8b
LLM_API_KEY=ollama
```

Pull the model first: `ollama pull qwen3:8b`

### Other providers

Change only `LLM_PROVIDER` and related vars — no code changes:

| Provider | `LLM_PROVIDER` | Notes |
| -------- | -------------- | ----- |
| Groq | `groq` | Free tier, fast |
| Gemini | `gemini` | Generous free tier |
| OpenAI | `openai` | Paid |

See `backend/.env.example` for full presets.

---

## API

| Method | Path | Description |
| ------ | ---- | ----------- |
| POST | `/api/v1/resumes/{id}/parse` | Parse (or re-parse) resume |
| GET | `/api/v1/resumes/{id}/parsed` | Fetch stored profile |

Both require JWT auth and ownership.

---

## Verification

```bash
ruff check . && mypy app
pytest -q
```

Integration tests use a **fake parser** — no live LLM calls in CI.

---

## How to try it

1. Start Ollama and pull `qwen3:8b`.
2. Set `backend/.env` (see above).
3. Upload a PDF, then `POST /resumes/{id}/parse`.
4. `GET /resumes/{id}/parsed` returns the cached profile.

```powershell
.\.venv\Scripts\uvicorn.exe app.main:app --reload
```

## What's next

Iteration 06 — interviews that consume parsed resume data for personalized
questions.
