# ── Stage 1: builder ──────────────────────────────────────────────────────────
FROM python:3.14-slim AS builder

ENV PIP_INDEX_URL=https://package-mirror.liara.ir/repository/pypi/simple \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install uv
RUN pip install uv

# Copy entire monorepo
COPY . .

# Install workspace dependencies
WORKDIR /app/UserService
RUN uv sync --no-dev

# ── Stage 2: runtime ──────────────────────────────────────────────────────────
FROM python:3.14-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# # Copy virtualenv from builder
COPY --from=builder /app/.venv /app/.venv

# Copy service files
COPY UserService/src ./src
COPY UserService/migrations ./migrations
COPY UserService/alembic.ini ./alembic.ini
COPY libs ./libs
COPY contracts ./contracts

COPY scripts/wait_for_services.sh /wait_for_services.sh

RUN chmod +x /wait_for_services.sh && \
    apt-get update && \
    apt-get install -y --no-install-recommends netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

EXPOSE 8000

CMD ["/bin/sh", "-c", "/wait_for_services.sh && alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8000"]