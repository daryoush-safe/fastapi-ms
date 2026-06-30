from __future__ import annotations

import re
import time
from collections.abc import Callable
from typing import Any

from fastapi import FastAPI
from prometheus_client import REGISTRY, Histogram
from prometheus_client.core import GaugeMetricFamily
from prometheus_client.registry import Collector
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.pool import Pool

_EXCLUDED = ["/metrics", "/healthz", "/readyz"]

db_query_duration_seconds = Histogram(
    "db_query_duration_seconds",
    "Time spent executing DB queries, by operation type.",
    labelnames=("operation",),
)

_OPERATION_RE = re.compile(r"^\s*(\w+)", re.IGNORECASE)

_KNOWN_OPERATIONS = {"select", "insert", "update", "delete"}

_TIMING_STACK_KEY = "_db_query_duration_start_stack"


def setup_metrics(app: FastAPI) -> None:
    Instrumentator(
        should_group_status_codes=True,
        excluded_handlers=_EXCLUDED,
    ).instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)


def _extract_operation(statement: str) -> str:
    match = _OPERATION_RE.match(statement)
    if not match:
        return "other"
    op = match.group(1).lower()
    return op if op in _KNOWN_OPERATIONS else "other"


def instrument_db_engine(engine: AsyncEngine) -> None:
    sync_engine = engine.sync_engine

    def _before_cursor_execute(
        conn: Any,
        cursor: Any,
        statement: str,
        parameters: Any,
        context: Any,
        executemany: bool,
    ) -> None:
        stack = conn.info.setdefault(_TIMING_STACK_KEY, [])
        stack.append(time.perf_counter())

    def _after_cursor_execute(
        conn: Any,
        cursor: Any,
        statement: str,
        parameters: Any,
        context: Any,
        executemany: bool,
    ) -> None:
        stack = conn.info.get(_TIMING_STACK_KEY)
        if not stack:
            return
        start = stack.pop()
        duration = time.perf_counter() - start
        operation = _extract_operation(statement)
        db_query_duration_seconds.labels(operation=operation).observe(duration)

    event.listen(sync_engine, "before_cursor_execute", _before_cursor_execute)
    event.listen(sync_engine, "after_cursor_execute", _after_cursor_execute)


class _DbPoolCollector(Collector):
    def __init__(self, pool_getter: Callable[[], Pool]) -> None:
        self._pool_getter = pool_getter

    def collect(self):  # type: ignore[no-untyped-def]
        gauge = GaugeMetricFamily(
            "db_active_connections",
            "Current DB connection pool state for this service.",
            labels=["state"],
        )
        try:
            pool = self._pool_getter()
        except Exception:
            gauge.add_metric(["used"], 0)
            gauge.add_metric(["idle"], 0)
            yield gauge
            return

        used = pool.checkedout()
        idle = pool.checkedin()
        gauge.add_metric(["used"], used)
        gauge.add_metric(["idle"], idle)
        yield gauge


def register_db_pool_gauge(pool_getter: Callable[[], Pool]) -> None:
    REGISTRY.register(_DbPoolCollector(pool_getter))
