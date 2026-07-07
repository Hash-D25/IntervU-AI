# 08 — Question Generator

## Goal

Generate structured interview questions from the interview plan, parsed resume,
and optional job description data. Use a **strategy per category** (DSA,
project, behavioral, CS fundamentals). **Generation code only** — not yet wired
to API routes or DB persistence.

## Scope

**In:** `QuestionGeneratorStrategy` protocol, four LLM strategies, category
selector, `QuestionGenerationService`, prompts, validation, config, unit tests.

**Out:** `POST /interviews/{id}/questions/generate`, persisting `Question` rows,
advancing session state during live interview.

---

## Architecture

```
QuestionGenerationContext
  ├── interview_plan
  ├── resume (ParsedResume)
  ├── job_description (ParsedJobDescription, optional)
  └── job_description_text (optional)
        │
        ▼
QuestionGenerationService.generate()
        │
        ├── select_question_categories(plan.question_mix)
        └── for each category → strategy.generate()
                ↓
        list[GeneratedQuestion]
```

### Strategy pattern

| Category | Strategy | Prompt file |
| -------- | -------- | ----------- |
| `dsa` | `DsaQuestionStrategy` | `interview_question_dsa.txt` |
| `project` | `ProjectQuestionStrategy` | `interview_question_project.txt` |
| `behavioral` | `BehavioralQuestionStrategy` | `interview_question_behavioral.txt` |
| `cs_fundamentals` | `CsFundamentalsQuestionStrategy` | `interview_question_cs_fundamentals.txt` |

All strategies extend `LlmQuestionStrategy` (`strategies/llm_base.py`) and call
`create_llm_provider(settings)`.

| Piece | Location |
| ----- | -------- |
| Schemas | `question_generation/schemas.py` |
| Protocol | `question_generation/protocols.py` |
| Orchestrator | `question_generation/service.py` |
| Factory | `question_generation/factory.py` |
| Category selector | `question_generation/selector.py` |
| Difficulty inference | `question_generation/difficulty.py` |
| Context builder | `question_generation/context_builder.py` |
| JSON parser | `question_generation/json_response.py` |

---

## Generated question shape

```json
{
  "text": "Walk me through how you designed ...",
  "category": "project",
  "expected_topics": ["architecture", "tradeoffs", "testing"],
  "difficulty": "easy|medium|hard",
  "evaluation_rubric": ["clarity", "depth", "evidence"]
}
```

Difficulty is suggested to the LLM based on JD seniority (`intern` → easy,
`junior/mid` → medium, `senior+` → hard).

---

## Question mix → categories

Example plan from Iteration 07:

```json
["resume_deep_dive", "technical_core", "project_walkthrough", "job_alignment"]
```

Maps to:

1. `project`
2. `dsa`
3. `project`
4. `cs_fundamentals`

Repeated `technical_core` entries alternate `dsa` and `cs_fundamentals`.

---

## Config

```env
QUESTION_GENERATOR=llm
```

Uses existing `LLM_PROVIDER`, `LLM_MODEL`, etc.

---

## Programmatic usage (current)

```python
from app.core.config import get_settings
from app.features.interview.question_generation.factory import (
    create_question_generator_strategies,
)
from app.features.interview.question_generation.schemas import QuestionGenerationContext
from app.features.interview.question_generation.service import QuestionGenerationService

strategies = create_question_generator_strategies(get_settings())
service = QuestionGenerationService(strategies)
result = await service.generate(context)
# result.questions → list[GeneratedQuestion]
```

No HTTP endpoint yet — Iteration 09 will expose this and persist questions.

---

## Verification

```bash
ruff check . && mypy app
pytest tests/unit/test_question_selector.py tests/unit/test_question_generation_service.py -q
```

Tests use a **fake LLM** — no live API calls in CI.

---

## Notes & gotchas

- One question is generated per `question_mix` entry (capped by
  `estimated_rounds * 2`).
- Strategies are replaceable: add a new class + register in `factory.py`.
- Prompts live under `app/ai/prompts/` as data, not inline strings.

## What's next

Iteration 09 — wire question generation to interview sessions: API endpoint,
persist `Question` rows, transition `session_state` from `ready` → `asking_intro`.
