import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from src.domain.models import MessageRole


class CreateThreadRequest(BaseModel):
    connection_id: uuid.UUID
    title: str | None = None


class ThreadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    connection_id: uuid.UUID
    title: str | None
    created_at: datetime
    updated_at: datetime
    last_message_at: datetime | None


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    role: MessageRole
    content: str | None
    sql: str | None
    created_at: datetime
    chart: dict | None = None
    columns: list | None = None
    rows: list | None = None


class SendMessageRequest(BaseModel):
    question: str = Field(min_length=1)
