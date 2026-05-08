from __future__ import annotations

import json

from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.ports.publisher import AbstractEventPublisher
from src.infrastructure.persistence.postgres.models.outbox_orm import OutboxORM

from contracts.topics import UserServiceTopics
from libs.shared_core.base_event import DomainEvent


class OutboxPublisher(AbstractEventPublisher):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def publish(self, event: DomainEvent) -> None:
        payload = self._serialize(event)
        record = OutboxORM(
            aggregate_id=str(self._extract_aggregate_id(event)),
            aggregate_type=UserServiceTopics.AGGREGATE_TYPE,  # → "user"
            event_type=event.event_type,
            payload=json.dumps(payload),
        )
        self._session.add(record)

    @staticmethod
    def _extract_aggregate_id(event: DomainEvent) -> object:
        return getattr(event, "user_id", event.event_id)

    @staticmethod
    def _serialize(event: DomainEvent) -> dict:
        import dataclasses

        return {
            k: str(v) if not isinstance(v, (str, int, float, bool, type(None))) else v
            for k, v in dataclasses.asdict(event).items()
        }
