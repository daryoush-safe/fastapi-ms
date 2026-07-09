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
    title: str | None
    created_at: datetime = field(default_factory=_utcnow)
    updated_at: datetime = field(default_factory=_utcnow)
    last_message_at: datetime | None = None


@dataclass
class ChatMessage:
    id: uuid.UUID
    thread_id: uuid.UUID
    role: MessageRole
    content: str | None  # natural-language turn (question or assistant answer)
    sql: str | None  # final SQL statement for assistant turns, else None
    created_at: datetime = field(default_factory=_utcnow)
