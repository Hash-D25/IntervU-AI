# features/evaluation

Answer evaluation.

Responsibility: score candidate answers across defined dimensions - technical
accuracy, completeness, communication, depth, and examples - producing
structured, explainable results.

- `protocols.py` - `AnswerEvaluator` contract (replaceable strategies)
- `strategies/llm_evaluator.py` - default LLM scorer
- `service.py` - orchestration + persistence
- Prompt: `app/ai/prompts/answer_evaluation.txt`

Evaluations run automatically when an answer is submitted. Interview-level
feedback reports are built in a later iteration.
