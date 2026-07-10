from __future__ import annotations

import logging
import uuid
from typing import Any, Awaitable, Callable

from src.application.dto import UpsertConnectionDTO
from src.application.services import ChatService

logger = logging.getLogger(__name__)

Handler = Callable[[dict[str, Any]], Awaitable[None]]


class ChatServiceEventRegistry:
    def __init__(self, chat_service: ChatService) -> None:
        self._chat_service = chat_service
        self._handlers: dict[str, Handler] = {
            "DatabaseConnectionRegistered": self._on_connection_registered,
            "ConnectionSchemaExtracted": self._on_schema_extracted,
        }

    def get(self, event_type: str) -> Handler | None:
        return self._handlers.get(event_type)

    async def _on_connection_registered(self, payload: dict[str, Any]) -> None:
        logger.info("Handling DatabaseConnectionRegistered: %s", payload.get("connection_id"))
        await self._chat_service.upsert_connection(
            UpsertConnectionDTO(
                connection_id=uuid.UUID(payload["connection_id"]),
                owner_id=uuid.UUID(payload["owner_id"]),
                title=payload.get("name"),
                engine=payload.get("engine"),
            )
        )

    async def _on_schema_extracted(self, payload: dict[str, Any]) -> None:
        logger.info("Handling ConnectionSchemaExtracted: %s", payload.get("connection_id"))
        await self._chat_service.upsert_connection(
            UpsertConnectionDTO(
                connection_id=uuid.UUID(payload["connection_id"]),
                owner_id=uuid.UUID(payload["owner_id"]),
                schema=payload["schema"],
            )
        )
