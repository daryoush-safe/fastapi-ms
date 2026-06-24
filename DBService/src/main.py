from contextlib import asynccontextmanager
from typing import AsyncIterator

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from shared_infra.observability import setup_observability
from sqlalchemy import text

from src.config import get_settings
from src.container import Container
from src.interfaces.http.api.v1.connections import router as connections_router
from src.interfaces.http.api.v1.query import router as query_router
from src.interfaces.http.exception_handlers import register_exception_handlers

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    await Container.startup()
    yield
    await Container.shutdown()


async def _check_db() -> bool:
    async with Container.engine().connect() as conn:
        await conn.execute(text("SELECT 1"))
    return True


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(connections_router, prefix="/api/v1")
    app.include_router(query_router, prefix="/api/v1")
    register_exception_handlers(app)

    setup_observability(
        app,
        service_name=settings.app_name,
        readiness_checks={"database": _check_db},
        log_level="DEBUG" if settings.debug else "INFO",
        json_logs=not settings.debug,
    )
    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug,
    )
