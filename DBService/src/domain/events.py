from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class DatabaseConnectionRegistered:
    connection_id: uuid.UUID
    owner_id: uuid.UUID
    name: str
    engine: str
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    event_type: str = field(default="DatabaseConnectionRegistered", init=False)


@dataclass(frozen=True)
class ConnectionSchemaExtracted:
    connection_id: uuid.UUID
    owner_id: uuid.UUID
    schema: str  # rendered schema text, forwarded verbatim to the ML service
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    event_type: str = field(default="ConnectionSchemaExtracted", init=False)
