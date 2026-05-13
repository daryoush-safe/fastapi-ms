FROM ghcr.io/mlflow/mlflow:latest

ENV PIP_INDEX_URL=https://mirror-pypi.runflare.com/simple \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install uv via mirror
RUN pip install uv

WORKDIR /mlflow/MLService

# Install dependencies from pyproject.toml
COPY pyproject.toml .
RUN uv pip install --system --no-cache \
    --index-url https://package-mirror.liara.ir/repository/pypi/simple \
    .

# Copy project files
COPY configs/ ./configs/
COPY scripts/ ./scripts/
COPY src/ ./src/
COPY fetch_california_housing.xlsx .