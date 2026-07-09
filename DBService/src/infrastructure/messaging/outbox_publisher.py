from __future__ import annotations

import dataclasses
import json

from shared_core.base_event import DomainEvent
from shared_infra.tracing import TRACE_CARRIER_KEY, inject_trace_context
from sqlalchemy.ext.asyncio import AsyncSession

from contracts.topics import DBServiceTopics
from src.domain.ports.publisher import IEventPublisher
from src.infrastructure.persistence.postgres.models.outbox_orm import OutboxORM


class OutboxPublisher(IEventPublisher):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def publish(self, event: DomainEvent) -> None:
        payload = self._serialize(event)
        payload[TRACE_CARRIER_KEY] = inject_trace_context()
        record = OutboxORM(
            aggregate_id=str(self._extract_aggregate_id(event)),
            aggregate_type=DBServiceTopics.AGGREGATE_TYPE,  # → "dbquery"
            event_type=event.event_type,
            payload=json.dumps(payload),
        )
        self._session.add(record)

    @staticmethod
    def _extract_aggregate_id(event: DomainEvent) -> object:
        return getattr(event, "connection_id", event.event_id)

    @staticmethod
    def _serialize(event: DomainEvent) -> dict:
        return {
            k: str(v) if not isinstance(v, (str, int, float, bool, type(None))) else v
            for k, v in dataclasses.asdict(event).items()
        }
