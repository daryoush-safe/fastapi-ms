from __future__ import annotations

import dataclasses
import json

from shared_core.base_event import DomainEvent
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from DBService.src.domain.ports.publisher import IEventPublisher
from DBService.src.infrastructure.persistence.postgres.models.outbox_orm import OutboxORM


class OutboxPublisher(IEventPublisher):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def publish(self, event: DomainEvent) -> None:
        async with self._session_factory() as session:
            payload = {
                k: str(v) if not isinstance(v, (str, int, float, bool, type(None))) else v
                for k, v in dataclasses.asdict(event).items()
            }
            record = OutboxORM(
                aggregate_id=str(getattr(event, "connection_id", event.event_id)),
                aggregate_type="dbquery",
                event_type=event.event_type,
                payload=json.dumps(payload),
            )
            session.add(record)
            await session.commit()
