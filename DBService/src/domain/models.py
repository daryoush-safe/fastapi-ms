from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class DatabaseConnection:
    id: uuid.UUID
    owner_id: uuid.UUID  # links to UserService user
    name: str
    engine: str  # "postgres" | "mysql" | "sqlite"
    dsn: str  # encrypted at rest
    schema_cache: dict | None
    is_active: bool


@dataclass
class QueryResult:
    connection_id: uuid.UUID
    columns: list[str]
    rows: list[list]
    executed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
