import uuid
from dataclasses import dataclass

from src.domain.models import DatabaseSchema, QueryResult


@dataclass
class ExtractSchemaDTO:
    connection_id: uuid.UUID
    owner_id: uuid.UUID


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


@dataclass
class ColumnDTO:
    name: str
    type: str
    nullable: bool
    primary_key: bool


@dataclass
class TableSchemaDTO:
    name: str
    columns: list[ColumnDTO]


@dataclass
class SchemaResultDTO:
    connection_id: uuid.UUID
    tables: list[TableSchemaDTO]

    @classmethod
    def from_domain(cls, schema: DatabaseSchema) -> "SchemaResultDTO":
        return cls(
            connection_id=schema.connection_id,
            tables=[
                TableSchemaDTO(
                    name=table.name,
                    columns=[
                        ColumnDTO(
                            name=col.name,
                            type=col.type,
                            nullable=col.nullable,
                            primary_key=col.primary_key,
                        )
                        for col in table.columns
                    ],
                )
                for table in schema.tables
            ],
        )
