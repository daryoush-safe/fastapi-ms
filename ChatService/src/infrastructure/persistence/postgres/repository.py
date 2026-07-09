from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models import ChatMessage, ChatThread
from src.domain.ports.repository import IChatMessageRepository, IChatThreadRepository
from src.infrastructure.persistence.postgres.models.message_orm import ChatMessageORM
from src.infrastructure.persistence.postgres.models.thread_orm import ChatThreadORM


class SqlAlchemyChatThreadRepository(IChatThreadRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, thread_id: uuid.UUID) -> ChatThread | None:
        result = await self._session.execute(
            select(ChatThreadORM).where(ChatThreadORM.id == thread_id)
        )
        orm = result.scalar_one_or_none()
        if orm is None:
            return None
        return self._to_domain(orm)

    async def list_by_user(self, user_id: uuid.UUID) -> list[ChatThread]:
        result = await self._session.execute(
            select(ChatThreadORM)
            .where(ChatThreadORM.user_id == user_id)
            .order_by(func.coalesce(ChatThreadORM.last_message_at, ChatThreadORM.created_at).desc())
        )
        return [self._to_domain(orm) for orm in result.scalars().all()]

    async def add(self, thread: ChatThread) -> None:
        self._session.add(self._to_orm(thread))

    async def update(self, thread: ChatThread) -> None:
        await self._session.merge(self._to_orm(thread))

    @staticmethod
    def _to_domain(orm: ChatThreadORM) -> ChatThread:
        return ChatThread(
            id=orm.id,
            user_id=orm.user_id,
            title=orm.title,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            last_message_at=orm.last_message_at,
        )

    @staticmethod
    def _to_orm(thread: ChatThread) -> ChatThreadORM:
        return ChatThreadORM(
            id=thread.id,
            user_id=thread.user_id,
            title=thread.title,
            created_at=thread.created_at,
            updated_at=thread.updated_at,
            last_message_at=thread.last_message_at,
        )


class SqlAlchemyChatMessageRepository(IChatMessageRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, message: ChatMessage) -> None:
        self._session.add(self._to_orm(message))

    async def list_by_thread(self, thread_id: uuid.UUID) -> list[ChatMessage]:
        result = await self._session.execute(
            select(ChatMessageORM)
            .where(ChatMessageORM.thread_id == thread_id)
            .order_by(ChatMessageORM.created_at)
        )
        return [self._to_domain(orm) for orm in result.scalars().all()]

    @staticmethod
    def _to_domain(orm: ChatMessageORM) -> ChatMessage:
        return ChatMessage(
            id=orm.id,
            thread_id=orm.thread_id,
            role=orm.role,
            content=orm.content,
            sql=orm.sql,
            created_at=orm.created_at,
        )

    @staticmethod
    def _to_orm(message: ChatMessage) -> ChatMessageORM:
        return ChatMessageORM(
            id=message.id,
            thread_id=message.thread_id,
            role=message.role,
            content=message.content,
            sql=message.sql,
            created_at=message.created_at,
        )
