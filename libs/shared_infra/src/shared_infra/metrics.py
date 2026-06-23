from __future__ import annotations

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

_EXCLUDED = ["/metrics", "/healthz", "/readyz"]


def setup_metrics(app: FastAPI) -> None:
    Instrumentator(
        should_group_status_codes=True,
        excluded_handlers=_EXCLUDED,
    ).instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)
