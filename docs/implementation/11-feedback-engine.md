# 11 - Feedback Engine

## Goal

Aggregate per-answer evaluations and interview history into a constructive,
actionable feedback report with strengths, weaknesses, recommendations, and a
learning roadmap.

## Scope

**In:** `FeedbackGenerator` protocol, `LlmFeedbackGenerator`, `FeedbackService`,
context builder from `execution_context`, persistence to `feedback_reports`,
generate/get API routes, tests.

**Out:** frontend UI, cross-interview analytics.

---

## Architecture

```
POST /interviews/{id}/feedback/generate
GET  /interviews/{id}/feedback
        │
        ▼
FeedbackService
        │
        ├── build_feedback_context(interview)
        │         └── evaluated answers from execution_context
        └── FeedbackGenerator.generate()
                  └── LlmFeedbackGenerator
```

| Piece | Location |
|-------|----------|
| Schemas | `features/feedback/schemas.py` |
| Protocol | `features/feedback/protocols.py` |
| Context | `features/feedback/context_builder.py` |
| LLM strategy | `features/feedback/strategies/llm_generator.py` |
| Service | `features/feedback/service.py` |
| ORM | `features/feedback/models.py` (pre-existing) |
| Prompt | `app/ai/prompts/feedback_generation.txt` |

---

## JSON output

```json
{
  "summary": "2-4 sentence synthesis",
  "strengths": ["..."],
  "weaknesses": ["..."],
  "recommendations": ["..."],
  "learning_roadmap": ["Week 1: ...", "Week 2: ..."],
  "overall_score": 8.2,
  "generator_name": "llm"
}
```

`overall_score` reflects the average of per-answer evaluation scores.

---

## Prerequisites

1. Interview completed (or at least one answered question with evaluation).
2. Evaluations stored in `execution_context` on each `SessionQuestion`.

---

## Config

```env
FEEDBACK_GENERATOR=llm
```

---

## API

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/interviews/{id}/feedback/generate` | Generate + persist report |
| GET | `/api/v1/interviews/{id}/feedback` | Fetch stored report |

---

## Verification

```bash
ruff check . && mypy app
pytest tests/unit/test_feedback_*.py -q
```

## What's next

Frontend feedback view and optional auto-generate on interview completion.
