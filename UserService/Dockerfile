# UserService/Dockerfile
FROM python:3.14-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_INDEX_URL=https://package-mirror.liara.ir/repository/pypi/simple \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# ── deps stage ────────────────────────────────────────────────────────────────
FROM python:3.14-slim AS deps

WORKDIR /app

RUN pip install --upgrade pip

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install .

# ── dev stage ─────────────────────────────────────────────────────────────────
FROM deps AS dev

RUN pip install ".[dev]"
COPY . .

# ── production stage ──────────────────────────────────────────────────────────
FROM deps AS prod

COPY src/ ./src/
COPY migrations/ ./migrations/
COPY alembic.ini .

RUN addgroup --system app && adduser --system --ingroup app app
USER app

CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]