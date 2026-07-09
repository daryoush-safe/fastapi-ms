import uuid
from dataclasses import dataclass
from datetime import datetime

from src.domain.models import ChatMessage, ChatThread, MessageRole


@dataclass
class CreateThreadDTO:
    user_id: uuid.UUID
    title: str | None = None


@dataclass
class SendMessageDTO:
    thread_id: uuid.UUID
    user_id: uuid.UUID
    question: str
    schema: str


@dataclass
class ListThreadsDTO:
    user_id: uuid.UUID


@dataclass
class GetMessagesDTO:
    thread_id: uuid.UUID
    user_id: uuid.UUID


@dataclass
class ThreadDTO:
    id: uuid.UUID
    title: str | None
    created_at: datetime
    updated_at: datetime
    last_message_at: datetime | None

    @classmethod
    def from_domain(cls, thread: ChatThread) -> "ThreadDTO":
        return cls(
            id=thread.id,
            title=thread.title,
            created_at=thread.created_at,
            updated_at=thread.updated_at,
            last_message_at=thread.last_message_at,
        )


@dataclass
class MessageDTO:
    id: uuid.UUID
    role: MessageRole
    content: str | None
    sql: str | None
    created_at: datetime

    @classmethod
    def from_domain(cls, message: ChatMessage) -> "MessageDTO":
        return cls(
            id=message.id,
            role=message.role,
            content=message.content,
            sql=message.sql,
            created_at=message.created_at,
        )
