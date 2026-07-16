from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class ChatThread:
    id: uuid.UUID
    user_id: uuid.UUID
    connection_id: uuid.UUID  # the DBService connection this thread queries
    title: str | None
    created_at: datetime = field(default_factory=_utcnow)
    updated_at: datetime = field(default_factory=_utcnow)
    last_message_at: datetime | None = None


@dataclass
class ConnectionRef:
    """Local replica of a DBService connection, fed by Kafka (CDC/outbox)."""

    connection_id: uuid.UUID
    owner_id: uuid.UUID
    title: str | None = None
    engine: str | None = None
    schema: str | None = None  # rendered schema text forwarded to the ML service
    updated_at: datetime = field(default_factory=_utcnow)


@dataclass
class ChatMessage:
    id: uuid.UUID
    thread_id: uuid.UUID
    role: MessageRole
    content: str | None
    sql: str | None
    chart: dict | None = None
    columns: list[str] | None = None
    rows: list[list] | None = None
    created_at: datetime = field(default_factory=_utcnow)
