# features/interview/follow_up

Adaptive follow-up question generation.

Flow:
1. Extract probe-worthy claims from the latest answer.
2. Decide whether depth/budget/phase policy allows a follow-up.
3. Generate one targeted probe (e.g. "Why Redis instead of Memcached?").

Interview execution asks the follow-up **before** advancing to the next phase.
Configurable:
- `FOLLOW_UP_GENERATOR=llm|none`
- `MAX_FOLLOW_UPS_PER_ANSWER` (depth per answer chain)
- `MAX_FOLLOW_UPS_PER_INTERVIEW`
- `FOLLOW_UP_ON_PHASES`
