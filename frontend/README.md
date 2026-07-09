# InterviewerAI - Frontend

Next.js (App Router) + TypeScript, organized **by feature**.

## Folder map

```
src/
├── app/          # routes (App Router): layouts, pages, route handlers
├── features/     # feature modules - the vertical slices of the UI
│   ├── resume/
│   ├── interview/
│   └── feedback/
├── components/   # shared, reusable presentational components
├── lib/          # API client + React Query setup (server state)
├── stores/       # Zustand stores (explicit client state)
└── types/        # shared TypeScript types (mirror backend DTOs)
```

## State management

- **Server state** → React Query (`lib/`): fetching, caching, mutations.
- **Client state** → Zustand (`stores/`): explicit UI/interview flow state.

Keep the two separate: don't cache server data in Zustand or hold ephemeral UI
state in React Query.

## Setup

```bash
# From frontend/
npm install
cp .env.local.example .env.local
npm run dev        # http://localhost:3000
```

## Common commands

```bash
npm run lint        # eslint
npm run typecheck   # tsc --noEmit
npm run build       # production build
```

> Note: app entry files (`app/layout.tsx`, `app/page.tsx`, `globals.css`) are
> added in the first frontend iteration.
