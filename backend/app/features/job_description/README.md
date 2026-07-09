# Job description analysis

Turn pasted job description text or a PDF into structured data - skills,
technologies, responsibilities, and seniority level.

Endpoints:
- `POST /analyze` - JSON body with `text`
- `POST /analyze/pdf` - multipart PDF upload

Processing lives under `processing/` with a pluggable `JobDescriptionAnalyzer`
protocol (LLM strategy today; rules or hybrid later).
