from contextlib import asynccontextmanager
from typing import AsyncIterator

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import get_settings
from src.container import Container
from src.interfaces.consumers.event_registry import UserServiceEventRegistry
from src.interfaces.consumers.kafka_handlers import UserServiceKafkaConsumer
from src.interfaces.http.api.v1.users import router as users_router
from src.interfaces.http.exception_handlers import register_exception_handlers

settings = get_settings()

_consumer: UserServiceKafkaConsumer | None = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    global _consumer
    registry = UserServiceEventRegistry(user_service=Container.user_service())
    _consumer = UserServiceKafkaConsumer(registry)
    await _consumer.start()
    yield
    await _consumer.stop()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(users_router, prefix="/api/v1")
    register_exception_handlers(app)
    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug,
    )
