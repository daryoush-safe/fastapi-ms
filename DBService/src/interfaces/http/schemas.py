import uuid
from typing import Literal

from pydantic import BaseModel, model_validator


class RegisterConnectionRequest(BaseModel):
    name: str
    engine: Literal["postgres", "mysql", "sqlite"]
    # Provide either a single-line DSN URL or the separated components below.
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
