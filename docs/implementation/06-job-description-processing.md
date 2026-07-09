# 06 - Job Description Processing

## Goal

Turn pasted job description text or a PDF into structured data - skills,
technologies, responsibilities, and seniority level - using a pluggable
analyzer. Output is returned as JSON (no persistence in this iteration).

## Scope

**In:** `JobDescriptionAnalyzer` protocol, `LlmJobDescriptionAnalyzer`,
`JobDescriptionProcessingService`, API routes for text and PDF input, prompts,
validation, config, unit + integration tests.

**Out:** storing analyzed JDs in the database, linking JD records to interviews
(structured JD is passed into interview creation as optional text today).

---

## Architecture

```
POST /job-descriptions/analyze          (JSON text)
POST /job-descriptions/analyze/pdf      (multipart PDF)
        │
        ▼
JobDescriptionProcessingService
        │
        ├── normalize / extract text (PDF → shared pdf_text helper)
        └── JobDescriptionAnalyzer.analyze()
                ↓
        ParsedJobDescriptionValidator
                ↓
        JobDescriptionAnalysisResponse (DTO)
```

### Analyzer layer

```
create_job_description_analyzer(settings)
        ↓
LlmJobDescriptionAnalyzer
        ↓
create_llm_provider(settings)   ← same factory as resume parsing
```

| Piece | Location |
| ----- | -------- |
| API DTOs | `features/job_description/schemas.py` |
| Router | `features/job_description/router.py` |
| Orchestrator | `features/job_description/processing/service.py` |
| Protocol | `features/job_description/processing/protocols.py` |
| LLM strategy | `processing/strategies/llm_analyzer.py` |
| Factory | `processing/factory.py` |
| Seniority enum + normalization | `processing/seniority.py` |
| Prompt | `app/ai/prompts/job_description_processing.txt` |
| PDF input | `processing/input.py` + `app/shared/pdf_text.py` |

---

## Structured output

```json
{
  "skills": ["..."],
  "technologies": ["..."],
  "responsibilities": ["..."],
  "seniority_level": "intern|entry|junior|mid|senior|...|unspecified",
  "analyzer_name": "llm"
}
```

Seniority aliases are normalized (e.g. `"Mid-level"` → `mid`). Skills and
technologies are deduplicated; technologies already listed under skills are
removed.

---

## Config

```env
JOB_DESCRIPTION_ANALYZER=llm
LLM_MAX_JD_CHARS=8000
JOB_DESCRIPTION_MAX_SIZE_MB=5
```

Uses the same `LLM_PROVIDER` / Groq / Ollama settings as resume parsing.

---

## API

| Method | Path | Description |
| ------ | ---- | ----------- |
| POST | `/api/v1/job-descriptions/analyze` | Analyze pasted text (min 50 chars) |
| POST | `/api/v1/job-descriptions/analyze/pdf` | Analyze uploaded PDF (max 5 MB) |

Both require JWT auth. No database writes.

---

## Verification

```bash
ruff check . && mypy app
pytest tests/unit/test_job_description_*.py tests/integration/test_job_description_processing.py -q
```

Integration tests use a **fake analyzer** - no live LLM calls in CI.

---

## How to try it

1. Authorize in Swagger (`POST /auth/login` → Bearer token).
2. **Text:** `POST /job-descriptions/analyze` with a JD body (50+ characters).
3. **PDF:** `POST /job-descriptions/analyze/pdf` with a selectable-text PDF.

---

## Notes & gotchas

- PDF must contain extractable text (not scanned image-only).
- `422` on `/analyze` usually means text shorter than 50 characters.
- `500` on first `/interviews` attempts was a separate migration issue (Iteration 07).

## What's next

Iteration 07 - interview session creation using a **parsed resume** and optional
job description context.
