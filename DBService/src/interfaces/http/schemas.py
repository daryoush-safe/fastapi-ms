import uuid
from typing import Literal

from pydantic import BaseModel


class RegisterConnectionRequest(BaseModel):
    name: str
    engine: Literal["postgres", "mysql", "sqlite"]
    dsn: str


class ConnectionResponse(BaseModel):
    id: uuid.UUID
    name: str
    engine: str
    is_active: bool


class QueryRequest(BaseModel):
    connection_id: uuid.UUID
    prompt: str


class QueryResponse(BaseModel):
    generated_sql: str
    columns: list[str]
    rows: list[list]
