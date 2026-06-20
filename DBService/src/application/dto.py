import uuid
from dataclasses import dataclass

from DBService.src.domain.models import QueryResult


@dataclass
class RunText2SQLCommand:
    connection_id: uuid.UUID
    prompt: str


@dataclass
class RegisterConnectionCommand:
    owner_id: uuid.UUID
    name: str
    engine: str
    dsn: str


@dataclass
class QueryResultDTO:
    generated_sql: str
    columns: list[str]
    rows: list[list]

    @classmethod
    def from_domain(cls, result: QueryResult) -> "QueryResultDTO":
        return cls(
            generated_sql=result.generated_sql,
            columns=result.columns,
            rows=result.rows,
        )
