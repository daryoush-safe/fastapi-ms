import uuid
from typing import Literal

from pydantic import BaseModel, ConfigDict, model_validator


class RegisterConnectionRequest(BaseModel):
    name: str
    engine: Literal["postgres", "mysql", "sqlite"]
    dsn: str | None = None
    host: str | None = None
    port: int | None = None
    username: str | None = None
    password: str | None = None
    database: str | None = None

    @model_validator(mode="after")
    def _require_dsn_or_components(self) -> "RegisterConnectionRequest":
        if not self.dsn and not self.database:
            raise ValueError("provide either 'dsn' or the separated connection components")
        return self


class ConnectionResponse(BaseModel):
    id: uuid.UUID
    name: str
    engine: str
    is_active: bool


class QueryRequest(BaseModel):
    connection_id: uuid.UUID
    sql: str


class QueryResponse(BaseModel):
    columns: list[str]
    rows: list[list]


class ColumnSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    type: str
    nullable: bool
    primary_key: bool


class TableSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    columns: list[ColumnSchema]


class ExtractSchemaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    connection_id: uuid.UUID
    tables: list[TableSchema]
