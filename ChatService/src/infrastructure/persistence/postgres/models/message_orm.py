import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.models import MessageRole
from src.infrastructure.persistence.postgres.models.base_orm import Base

_role_enum = Enum(
    MessageRole,
    name="message_role",
    schema="chatservice",
    values_callable=lambda enum: [member.value for member in enum],
)


class ChatMessageORM(Base):
    __tablename__ = "chat_messages"
    __table_args__ = {"schema": "chatservice"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    thread_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chatservice.chat_threads.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[MessageRole] = mapped_column(_role_enum, nullable=False)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    sql: Mapped[str | None] = mapped_column(Text, nullable=True)
    chart: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    columns: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)
    rows: Mapped[list[list[Any]] | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
