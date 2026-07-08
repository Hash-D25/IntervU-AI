# 14 — Interview Memory

## Goal

Rebuild a compact interview memory after each answer so later questions and
follow-ups can reference earlier statements — e.g. **"You mentioned JWT earlier..."**.

## Scope

**In:** memory schemas, builder abstraction, session rebuild strategy, persist on
`SessionContext`, inject into question + follow-up prompts, config, tests.

**Out:** vector store / separate memory DB, LLM summarization, frontend memory UI.

---

## Stored fields

| Field | Source |
|-------|--------|
| Previous answers | Answer excerpts + question stubs |
| Discussed topics | Expected topics, probed claims, tech mentions |
| Strengths / weak areas | Evaluation strengths / improvements |
| Notable mentions | Claims + tech tokens for callbacks |
| Dimension averages | Rolling averages from evaluations |

---

## Architecture

```
submit_answer
  → evaluate
  → memory_builder.rebuild(session)   # cheap, no LLM
  → persist SessionContext.memory in execution_context JSONB
  → question generation / follow-up prompt get interview_memory
```

### Abstraction (future persistence)

| Contract | Role |
|----------|------|
| `InterviewMemoryBuilder` | Rebuild from live session (v1: `session`) |
| `InterviewMemoryStore` | Reserved for DB / vector load+save |

Config: `INTERVIEW_MEMORY=session|none`.

| Setting | Default |
|---------|---------|
| `INTERVIEW_MEMORY` | `session` |
| `INTERVIEW_MEMORY_MAX_ANSWERS` | `8` |
| `INTERVIEW_MEMORY_EXCERPT_CHARS` | `280` |

`build_execution_hints` remains for diversity (covered projects / topics).
Memory is semantic recall for natural callbacks — they are complementary.

---

## Key files

| Piece | Location |
|-------|----------|
| Schemas | `features/interview/memory/schemas.py` |
| Protocols | `features/interview/memory/protocols.py` |
| Session builder | `features/interview/memory/builder.py` |
| Factory | `features/interview/memory/factory.py` |
| Prompt payload | `features/interview/memory/prompt_context.py` |
| Session field | `SessionContext.memory` |
| Wiring | `execution/service.py`, `dependencies.py` |

---

## Verification

```bash
cd backend
ruff check app/features/interview/memory app/features/interview/execution/service.py
pytest tests/unit/test_interview_memory.py -q
```
