from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models import ChatMessage, ChatThread, ConnectionRef
from src.domain.ports.repository import (
    IChatMessageRepository,
    IChatThreadRepository,
    IConnectionRefRepository,
)
from src.infrastructure.persistence.postgres.models.connection_orm import ConnectionRefORM
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
            connection_id=orm.connection_id,
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
            connection_id=thread.connection_id,
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
            chart=orm.chart,
            columns=orm.columns,
            rows=orm.rows,
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
            chart=message.chart,
            columns=message.columns,
            rows=message.rows,
            created_at=message.created_at,
        )


class SqlAlchemyConnectionRefRepository(IConnectionRefRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, connection_id: uuid.UUID) -> ConnectionRef | None:
        orm = await self._session.get(ConnectionRefORM, connection_id)
        if orm is None:
            return None
        return self._to_domain(orm)

    async def upsert(self, ref: ConnectionRef) -> None:
        await self._session.merge(self._to_orm(ref))

    @staticmethod
    def _to_domain(orm: ConnectionRefORM) -> ConnectionRef:
        return ConnectionRef(
            connection_id=orm.connection_id,
            owner_id=orm.owner_id,
            title=orm.title,
            engine=orm.engine,
            schema=orm.schema,
            updated_at=orm.updated_at,
        )

    @staticmethod
    def _to_orm(ref: ConnectionRef) -> ConnectionRefORM:
        return ConnectionRefORM(
            connection_id=ref.connection_id,
            owner_id=ref.owner_id,
            title=ref.title,
            engine=ref.engine,
            schema=ref.schema,
            updated_at=ref.updated_at,
        )
