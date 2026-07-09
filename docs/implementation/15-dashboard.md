# 15 - Dashboard

## Goal

Give candidates a readable overview of mock interview performance: history,
strengths, weaknesses, category scores, and progress over time.

## Scope

**In:** `GET /dashboard`, `GET /interviews/` summary list, frontend `/dashboard`
with reusable components, tests, docs.

**Out:** PDF export, team analytics, advanced charting library.

---

## API

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/dashboard` | Cross-interview summary |
| GET | `/interviews/` | Interview history cards |

`DashboardSummary` includes:

- `interview_history`
- `strengths` / `weaknesses` (from feedback reports)
- `category_scores` (from execution evaluations)
- `dimension_averages`
- `progress_over_time`

Scores fall back to execution-context averages when feedback is missing.

---

## Frontend

Route: `/dashboard`

Reusable components under `features/dashboard/components/`:

- `DashboardCard`, `StatCard`
- `InterviewHistoryList`
- `InsightList` (strengths / weaknesses)
- `CategoryScores`, `DimensionScores`, `ProgressChart`

---

## Verification

```bash
cd backend
ruff check app/features/dashboard
pytest tests/unit/test_dashboard_aggregator.py tests/integration/test_dashboard.py -q
```

```bash
cd frontend
npm run build
```
