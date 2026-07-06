# src/features

Feature modules — vertical UI slices mirroring backend capabilities.

Each feature owns its components, hooks, and local state:

```
<feature>/
├── components/   # feature-specific UI
├── hooks/        # React Query hooks + feature logic
└── types.ts      # feature-local types
```

Capabilities: `resume/`, `interview/`, `feedback/`. Shared UI lives in
`src/components`; cross-cutting API/query setup lives in `src/lib`.
