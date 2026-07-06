# features/interview

Interview session lifecycle and dynamic question flow.

Responsibility: manage a session as an **explicit state machine** (not raw chat
history), driving contextual questions and adaptive follow-ups based on the
candidate's answers, resume, and target job description.

The actual conversational reasoning is delegated to `app/ai/graphs`; this feature
owns session state, persistence, and orchestration.
