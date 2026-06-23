from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable

from fastapi import APIRouter
from fastapi.responses import JSONResponse

ReadinessCheck = Callable[[], Awaitable[bool]]


async def _run(check: ReadinessCheck) -> bool:
    try:
        return bool(await check())
    except Exception:
        return False


def build_health_router(
    readiness_checks: dict[str, ReadinessCheck] | None = None,
) -> APIRouter:
    router = APIRouter(tags=["health"])
    checks = readiness_checks or {}

    @router.get("/healthz", include_in_schema=False)
    async def healthz() -> dict[str, str]:
        return {"status": "alive"}

    @router.get("/readyz", include_in_schema=False)
    async def readyz() -> JSONResponse:
        if not checks:
            return JSONResponse({"status": "ready", "checks": {}})

        names = list(checks)
        results = await asyncio.gather(*(_run(checks[n]) for n in names))
        statuses = {n: ("ok" if ok else "fail") for n, ok in zip(names, results)}
        all_ok = all(results)
        return JSONResponse(
            {"status": "ready" if all_ok else "not_ready", "checks": statuses},
            status_code=200 if all_ok else 503,
        )

    return router
