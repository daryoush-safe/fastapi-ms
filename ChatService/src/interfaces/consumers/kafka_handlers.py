from __future__ import annotations

import logging
from typing import Any

from shared_infra.kafka_consumer_base import BaseKafkaConsumer

from contracts.topics import DBServiceTopics
from src.config import get_settings
from src.interfaces.consumers.event_registry import ChatServiceEventRegistry

logger = logging.getLogger(__name__)
settings = get_settings()


class ChatServiceKafkaConsumer(BaseKafkaConsumer):
    def __init__(self, registry: ChatServiceEventRegistry) -> None:
        super().__init__(
            topics=[DBServiceTopics.CONNECTION_TOPIC],
            bootstrap_servers=settings.kafka_bootstrap_servers,
            group_id="chat_service_group",
        )
        self._registry = registry

    async def handle(self, event_type: str, payload: dict[str, Any]) -> None:
        handler = self._registry.get(event_type)
        if handler is None:
            logger.warning("No handler for event_type=%s", event_type)
            return
        await handler(payload)
