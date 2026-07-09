# 13 - Follow-up Questions

## Goal

Generate adaptive probing follow-ups from candidate answers by extracting claims
and asking focused questions - e.g. **"We used Redis." → "Why Redis instead of Memcached?"**

## Scope

**In:** claim extraction, follow-up generation, depth/budget policy, deferred phase
advance so follow-ups stay in the same phase, execution wiring, tests, prompts.

**Out:** multi-turn debate loops, interviewer TTS, frontend follow-up UI polish.

---

## Behavior

```
Answer submitted
  → evaluate
  → extract claims
  → if policy allows: ask follow-up in same phase
  → else: advance to next phase / next root question
```

### Example

Candidate: *“We used Redis.”*  
Follow-up: *“Why Redis instead of Memcached?”*

### Configurable depth

| Setting | Default | Meaning |
|---------|---------|---------|
| `FOLLOW_UP_GENERATOR` | `llm` | `llm` or `none` |
| `MAX_FOLLOW_UPS_PER_ANSWER` | `1` | Max probes in one answer chain |
| `MAX_FOLLOW_UPS_PER_INTERVIEW` | `3` | Global interview ceiling |
| `FOLLOW_UP_ON_PHASES` | `resume,projects,cs_fundamentals,behavioral` | Phases that can probe |

Introduction / final skip follow-ups by default.

---

## Architecture

```
InterviewExecutionService.submit_answer
        │
        ├── InterviewEngine.submit_answer   # marks answered, does NOT advance
        ├── AnswerEvaluationService
        └── FollowUpService.decide
                  ├── ClaimExtractor (LLM)
                  └── FollowUpGenerator (LLM)
                        │
              ┌─────────┴──────────┐
              ▼                    ▼
        attach follow-up     advance_after_answer
        (same phase)         + next root question
```

| Piece | Location |
|-------|----------|
| Schemas | `follow_up/schemas.py` |
| Protocols | `follow_up/protocols.py` |
| Service / policy | `follow_up/service.py` |
| LLM strategies | `follow_up/strategies/` |
| Prompts | `claim_extraction.txt`, `follow_up_generation.txt` |
| Engine | `submit_answer` defers; `advance_after_answer` is explicit |

Session fields on each question: `is_follow_up`, `parent_question_id`,
`follow_up_depth`, `probed_claims`. Follow-ups do **not** consume the phase root quota.

---

## Verification

```bash
cd backend
ruff check .
mypy app
pytest tests/unit/test_follow_up_service.py tests/integration/test_follow_up_generation.py tests/unit/test_interview_engine.py -q
```

## What's next

Tune claim quality / score gates, and surface follow-up badges in the interview UI.
