from __future__ import annotations

import logging
from typing import Any

from src.config import get_settings
from src.interfaces.consumers.event_registry import UserServiceEventRegistry

from contracts.topics import SubscriptionServiceTopics
from libs.shared_infra.kafka_consumer_base import BaseKafkaConsumer

logger = logging.getLogger(__name__)
settings = get_settings()


class UserServiceKafkaConsumer(BaseKafkaConsumer):
    def __init__(self, registry: UserServiceEventRegistry) -> None:
        super().__init__(
            topics=[SubscriptionServiceTopics.TOPIC],
            bootstrap_servers=settings.kafka_bootstrap_servers,
            group_id="user_service_group",
        )
        self._registry = registry

    async def handle(self, event_type: str, payload: dict[str, Any]) -> None:
        handler = self._registry.get(event_type)
        if handler is None:
            logger.warning("No handler for event_type=%s", event_type)
            return
        await handler(payload)
