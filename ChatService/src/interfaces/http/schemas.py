import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from src.domain.models import MessageRole


class CreateThreadRequest(BaseModel):
    title: str | None = None


class ThreadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
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


class SendMessageRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    question: str = Field(min_length=1)
    # DB schema text forwarded verbatim to the ML service. Aliased to "schema"
    # to avoid shadowing pydantic's BaseModel.schema attribute.
    schema_text: str = Field(alias="schema", min_length=1)
