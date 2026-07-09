# features/feedback

Feedback report generation.

Responsibility: aggregate per-answer evaluations and interview history into an
actionable coach-style report - strengths, weaknesses, recommendations, and a
learning roadmap.

- `protocols.py` - `FeedbackGenerator` contract (replaceable strategies)
- `strategies/llm_generator.py` - default LLM report generator
- `context_builder.py` - builds input from `execution_context` + evaluations
- `service.py` - orchestration + persistence to `feedback_reports`
- Prompt: `app/ai/prompts/feedback_generation.txt`

Tone is **coach, not judge**: prefer constructive, actionable guidance.
