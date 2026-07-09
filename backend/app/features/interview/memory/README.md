# features/interview/memory

Rolling interview memory rebuilt from answered questions.

Stores (compactly):
- previous answer excerpts
- discussed topics
- strengths / weak areas
- notable mentions (for callbacks like "You mentioned JWT earlier...")

Abstraction:
- `InterviewMemoryBuilder` - rebuild from `SessionContext` (v1: session)
- `InterviewMemoryStore` - reserved for future DB / vector persistence

Config: `INTERVIEW_MEMORY=session|none`
