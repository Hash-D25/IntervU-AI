# features/interview

Interview session lifecycle and dynamic question flow.

Responsibility: manage a session as an **explicit state machine** (not raw chat
history), driving contextual questions and adaptive follow-ups based on the
candidate's answers, parsed resume, and optional target job description.

This iteration creates interview sessions, stores metadata and an interview plan,
and seeds a future-ready state machine without generating questions yet.
