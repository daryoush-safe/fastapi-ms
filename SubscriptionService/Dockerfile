FROM python:3.14-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_INDEX_URL=https://package-mirror.liara.ir/repository/pypi/simple \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# ─────────────────────────────────────────────────────────────
# deps
# ─────────────────────────────────────────────────────────────
FROM base AS deps

RUN pip install --upgrade pip

COPY pyproject.toml .
COPY src ./src

RUN pip install .

# ─────────────────────────────────────────────────────────────
# dev
# ─────────────────────────────────────────────────────────────
FROM deps AS dev

RUN pip install ".[dev]"

# ─────────────────────────────────────────────────────────────
# prod
# ─────────────────────────────────────────────────────────────
FROM deps AS prod

COPY migrations ./migrations
COPY alembic.ini .

RUN addgroup --system app && adduser --system --ingroup app app

USER app

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]