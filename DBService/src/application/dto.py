import uuid
from dataclasses import dataclass

from src.domain.models import QueryResult


@dataclass
class RunText2SQLDTO:
    connection_id: uuid.UUID
    owner_id: uuid.UUID
    sql: str


@dataclass
class RegisterConnectionDTO:
    owner_id: uuid.UUID
    name: str
    engine: str
    dsn: str | None = None
    host: str | None = None
    port: int | None = None
    username: str | None = None
    password: str | None = None
    database: str | None = None


@dataclass
class QueryResultDTO:
    columns: list[str]
    rows: list[list]

    @classmethod
    def from_domain(cls, result: QueryResult) -> "QueryResultDTO":
        return cls(
            columns=result.columns,
            rows=result.rows,
        )
