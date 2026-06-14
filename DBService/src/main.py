from contextlib import asynccontextmanager
from typing import AsyncIterator

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from DBService.src.config import get_settings
from DBService.src.container import Container
from DBService.src.interfaces.http.api.v1.connections import router as connections_router
from DBService.src.interfaces.http.api.v1.query import router as query_router
from DBService.src.interfaces.http.exception_handlers import register_exception_handlers

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    await Container.startup()
    yield
    await Container.shutdown()


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
    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "DBService.src.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug,
    )
