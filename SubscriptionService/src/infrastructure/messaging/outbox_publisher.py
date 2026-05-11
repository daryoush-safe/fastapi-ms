from __future__ import annotations

import json

from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.ports.publisher import AbstractEventPublisher
from src.infrastructure.persistence.postgres.models.outbox_orm import OutboxORM

from contracts.topics import SubscriptionServiceTopics
from libs.shared_core.base_event import DomainEvent


class OutboxPublisher(AbstractEventPublisher):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def publish(self, event: DomainEvent) -> None:
        record = OutboxORM(
            aggregate_id=str(getattr(event, "subscription_id", event.event_id)),
            aggregate_type=SubscriptionServiceTopics.AGGREGATE_TYPE,  # → "subscription"
            event_type=event.event_type,
            payload=json.dumps(self._serialize(event)),
        )
        self._session.add(record)

    @staticmethod
    def _serialize(event: DomainEvent) -> dict:
        import dataclasses

        data = {
            k: str(v) if not isinstance(v, (str, int, float, bool, type(None))) else v
            for k, v in dataclasses.asdict(event).items()
        }
        data["event_type"] = event.event_type
        return data
