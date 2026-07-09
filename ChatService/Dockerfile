# ── Stage 1: builder ──────────────────────────────────────────────────────────
FROM python:3.14-slim AS builder

WORKDIR /app

RUN pip install uv

# Copy entire monorepo so uv can resolve workspace deps
COPY . .

WORKDIR /app/ChatService
RUN uv sync --no-dev

# ── Stage 2: runtime ──────────────────────────────────────────────────────────
FROM python:3.14-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Virtualenv from builder (workspace root)
COPY --from=builder /app/.venv /app/.venv

# Service source — /app/src so `from src.*` imports resolve (PYTHONPATH=/app)
COPY ChatService/src           ./src

# Alembic (placed at /app so alembic.ini script_location=migrations resolves)
COPY ChatService/migrations   ./migrations
COPY ChatService/alembic.ini  ./alembic.ini

# Shared workspace libs — required by editable venv installs
COPY libs      ./libs
COPY contracts ./contracts

RUN apt-get update && \
    apt-get install -y --no-install-recommends netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

EXPOSE 8004

CMD ["/bin/sh", "-c", \
     "while ! nc -z ${DB_HOST:-postgres} ${DB_PORT:-5432}; do sleep 2; done && \
      alembic upgrade head && \
      uvicorn src.main:app --host 0.0.0.0 --port 8004"]
