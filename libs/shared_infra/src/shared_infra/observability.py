from __future__ import annotations

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine

from shared_infra.health import ReadinessCheck, build_health_router
from shared_infra.logging import configure_logging
from shared_infra.metrics import register_db_pool_gauge, setup_metrics
from shared_infra.middleware import RequestContextMiddleware
from shared_infra.tracing import setup_tracer


def setup_observability(
    app: FastAPI,
    *,
    service_name: str,
    engine: AsyncEngine | None = None,
    readiness_checks: dict[str, ReadinessCheck] | None = None,
    log_level: str = "INFO",
    json_logs: bool = True,
) -> None:
    configure_logging(service_name, level=log_level, json_logs=json_logs)
    app.add_middleware(RequestContextMiddleware)
    app.include_router(build_health_router(readiness_checks))
    setup_metrics(app)
    if engine is not None:
        setup_tracer(app, service_name=service_name, engine=engine)
        register_db_pool_gauge(lambda: engine.pool)
