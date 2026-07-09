FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md alembic.ini ./
COPY app ./app
COPY migrations ./migrations
COPY scripts/start.sh ./scripts/start.sh

RUN pip install --upgrade pip \
    && pip install . \
    && chmod +x ./scripts/start.sh

EXPOSE 8000

CMD ["./scripts/start.sh"]
