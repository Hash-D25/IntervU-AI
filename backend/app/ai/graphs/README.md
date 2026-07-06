# ai/graphs

LangGraph state machines that drive the interview.

Responsibility: model the interview as **explicit states and transitions**
(e.g. ask → listen → analyze → follow-up / next-topic → evaluate), rather than
relying on conversation history alone.

Graph nodes call the `providers` interface and use `prompts`; they hold no
persistence logic (that stays in the interview feature).
