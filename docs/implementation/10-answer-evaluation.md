# 10 — Answer Evaluation

## Goal

Score each interview answer across five structured dimensions and return
explainable results. Evaluators are pluggable so scoring models can be swapped
later.

## Scope

**In:** `AnswerEvaluator` protocol, `LlmAnswerEvaluator`, `AnswerEvaluationService`,
`answer_evaluations` persistence, automatic evaluation on answer submit, GET
evaluation endpoint, unit + integration tests.

**Out:** interview-level feedback reports (future iteration).

---

## Evaluation dimensions

| Dimension | What it measures |
|-----------|------------------|
| `technical_accuracy` | Correctness of technical claims |
| `completeness` | Coverage of expected topics / rubric |
| `communication` | Clarity and structure |
| `depth` | Level of understanding beyond surface |
| `examples` | Use of concrete evidence from experience |

Each dimension returns `score` (0–10) and a short `rationale`.

---

## Architecture

```
POST /interviews/{id}/execution/answer
        │
        ▼
InterviewExecutionService.submit_answer
        │
        ├── persist answer
        ├── AnswerEvaluationService.evaluate_and_persist()
        │         └── AnswerEvaluator.evaluate()  (protocol)
        └── attach evaluation to SessionQuestion in execution_context

GET /interviews/{id}/questions/{question_id}/evaluation
        └── AnswerEvaluationService.get_for_question()
```

| Piece | Location |
|-------|----------|
| Schemas | `features/evaluation/schemas.py` |
| Protocol | `features/evaluation/protocols.py` |
| LLM strategy | `features/evaluation/strategies/llm_evaluator.py` |
| Factory | `features/evaluation/factory.py` |
| Service | `features/evaluation/service.py` |
| ORM | `features/evaluation/models.py` |
| Prompt | `app/ai/prompts/answer_evaluation.txt` |
| Migration | `migrations/versions/0008_answer_evaluations.py` |

---

## Structured response

```json
{
  "overall_score": 7.5,
  "scores": [
    {
      "dimension": "technical_accuracy",
      "score": 8.0,
      "rationale": "JWT and bcrypt usage described correctly."
    }
  ],
  "strengths": ["Clear structure"],
  "improvements": ["Mention token expiry handling"],
  "evaluator_name": "llm"
}
```

**Phase-aware scoring:** dimension weights vary by interview phase (introduction
emphasizes communication/completeness; projects/cs emphasize technical depth).
Contradictory improvements (e.g. "add LeetCode counts" when already stated) are
filtered post-generation.

---

## Config

```env
ANSWER_EVALUATOR=llm
```

Uses existing `LLM_PROVIDER`, `LLM_MODEL`, etc.

---

## API

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/interviews/{id}/execution/answer` | Submit answer; returns evaluation on answered question |
| GET | `/api/v1/interviews/{id}/questions/{qid}/evaluation` | Fetch stored evaluation |

---

## Verification

```bash
ruff check . && mypy app
pytest tests/unit/test_answer_evaluation_*.py tests/integration/test_interview_execution.py -q
```

Apply migration:

```powershell
cd backend
.\.venv\Scripts\alembic.exe upgrade head
```

## What's next

Aggregate per-answer evaluations into an interview-level feedback report.
