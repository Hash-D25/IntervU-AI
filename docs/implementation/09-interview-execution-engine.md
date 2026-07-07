# 09 — Interview Execution Engine

## Goal

Run a live interview session with an **explicit phase state machine** — no hidden
state. The engine tracks the current question, previous questions, full session
context, and allowed phase transitions.

## Scope

**In:** `InterviewPhase` states, pure `InterviewEngine`, `InterviewExecutionService`,
phase question provider, `execution_context` persistence, start/answer API routes,
unit + integration tests.

**Out:** answer evaluation/scoring, follow-up generation, voice/STT, frontend UI.

---

## Phase state machine

```
INTRODUCTION → RESUME → PROJECTS → CS_FUNDAMENTALS → BEHAVIORAL → FINAL
```

Phases vary by `interview_type`:

| Type | Phases |
|------|--------|
| `technical` | INTRODUCTION → RESUME → PROJECTS → CS_FUNDAMENTALS → FINAL |
| `behavioral` | INTRODUCTION → RESUME → BEHAVIORAL → FINAL |
| `mixed` | All six phases |

Within each phase (except `FINAL`), one question is asked by default. After the
answer is submitted, the engine advances to the next phase and generates the next
question automatically.

**Phase diversity:** resume questions compare projects or cover breadth; projects
phase deep-dives a different project not already asked about; CS fundamentals
avoids repeated topics and prefers the candidate's actual stack.

---

## Architecture

```
POST /interviews/{id}/execution/start
POST /interviews/{id}/execution/answer
GET  /interviews/{id}/execution
        │
        ▼
InterviewExecutionService
        │
        ├── InterviewEngine (pure transitions)
        ├── PhaseQuestionProvider (intro = deterministic, others = LLM)
        └── Interview / Question / Answer repositories
```

### Explicit session context (`execution_context` JSONB)

All engine state is stored in `interviews.execution_context`:

| Field | Purpose |
|-------|---------|
| `status` | `not_started` / `in_progress` / `completed` |
| `phase` | Current `InterviewPhase` |
| `phase_sequence` | Frozen phase order for this interview |
| `questions_per_phase` | Quota per phase |
| `questions` | All asked questions + answers |
| `awaiting_answer` | Whether current question needs an answer |

No implicit state outside this blob.

| Piece | Location |
|-------|----------|
| Schemas | `execution/schemas.py` |
| State machine rules | `execution/state_machine.py` |
| Pure engine | `execution/engine.py` |
| Service | `execution/service.py` |
| Question provider | `execution/question_provider.py` |
| Migration | `migrations/versions/0007_interview_execution_engine.py` |

---

## API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/interviews/{id}/execution` | Current snapshot |
| POST | `/api/v1/interviews/{id}/execution/start` | Start session + first question |
| POST | `/api/v1/interviews/{id}/execution/answer` | Submit answer, advance phase |

### Snapshot response

```json
{
  "status": "in_progress",
  "phase": "introduction",
  "current_question": { "text": "...", "phase": "introduction", "answered": false },
  "previous_questions": [],
  "allowed_transitions": ["introduction"],
  "session_context": { "...": "full explicit state" }
}
```

---

## Prerequisites

1. Interview created (`POST /interviews/`).
2. Resume parsed (`parse_status: completed`).
3. Migration applied:

```powershell
cd backend
.\.venv\Scripts\alembic.exe upgrade head
```

---

## Verification

```bash
ruff check . && mypy app
pytest tests/unit/test_interview_engine.py tests/integration/test_interview_execution.py -q
```

---

## How to try it

1. Create an interview (Iteration 07).
2. `POST /interviews/{id}/execution/start` — returns intro question.
3. `POST /interviews/{id}/execution/answer` with `{ "transcript": "..." }`.
4. Repeat until `status` is `completed` and `phase` is `final`.

## What's next

Answer evaluation per submitted response, then interview-level feedback reports.
