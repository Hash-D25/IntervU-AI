# InterviewerAI — Implementation Docs

A living record of **what we built, why, and how** — written iteration by
iteration so anyone (including future-you in an interview) can understand the
whole system by reading in order.

## How this is organized

One file per phase/iteration, kept small and self-contained:

| Doc | Covers |
| --- | ------ |
| [`implementation/00-project-setup.md`](./implementation/00-project-setup.md) | Repo scaffolding, tooling, dependency choices. |
| [`implementation/01-foundation.md`](./implementation/01-foundation.md) | Runnable backend + frontend foundation (config, DB, DI, app factory, health, migrations). |
| [`implementation/02-database-layer.md`](./implementation/02-database-layer.md) | Entities, ORM models, mixins, base + concrete repositories, initial migration, tests. |
| [`implementation/03-authentication.md`](./implementation/03-authentication.md) | JWT auth, rotating refresh tokens, register/login/logout, protected routes. |

New iterations append a new numbered file here.

## Conventions used in these docs

Each iteration doc follows the same shape:

1. **Goal** — what this iteration delivers in one sentence.
2. **Scope** — explicitly in and out.
3. **Architecture & decisions** — the *why*, with tradeoffs and alternatives.
4. **File-by-file walkthrough** — every file created, what it does.
5. **Commands & verification** — how it was checked, with results.
6. **How to run** — reproducible steps.
7. **Notes & gotchas** — anything non-obvious for later.

## Project rules these docs uphold

- Files < 300 lines, functions < 50 lines.
- Strict typing everywhere (mypy strict, TS strict).
- Routes validate + delegate; business logic in services; DB access in repositories.
- AI kept behind interfaces; prompts stored as data; providers replaceable.
- Config from environment variables only.
- Every important feature ships with tests.
- Tone of the product: **coach, not judge**.
