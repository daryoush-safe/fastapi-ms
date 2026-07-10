from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

from shared_core.base_aggregate import AggregateRoot

from src.domain.events import ConnectionSchemaExtracted, DatabaseConnectionRegistered


@dataclass(eq=False)
class DatabaseConnection(AggregateRoot):
    id: uuid.UUID
    owner_id: uuid.UUID  # links to UserService user
    name: str
    engine: str  # "postgres" | "mysql" | "sqlite"
    dsn: str  # encrypted at rest
    schema_cache: dict | None
    is_active: bool

    def record_registered(self) -> None:
        self.record_event(
            DatabaseConnectionRegistered(
                connection_id=self.id,
                owner_id=self.owner_id,
                name=self.name,
                engine=self.engine,
            )
        )

    def apply_schema(self, schema_cache: dict, schema_text: str) -> None:
        self.schema_cache = schema_cache
        self.record_event(
            ConnectionSchemaExtracted(
                connection_id=self.id,
                owner_id=self.owner_id,
                schema=schema_text,
            )
        )


@dataclass
class QueryResult:
    connection_id: uuid.UUID
    columns: list[str]
    rows: list[list]
    executed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ColumnInfo:
    name: str
    type: str
    nullable: bool
    primary_key: bool


@dataclass
class TableSchema:
    name: str
    columns: list[ColumnInfo]


@dataclass
class DatabaseSchema:
    connection_id: uuid.UUID
    tables: list[TableSchema]
