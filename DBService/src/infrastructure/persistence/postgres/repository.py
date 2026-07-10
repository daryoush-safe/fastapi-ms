from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models import DatabaseConnection
from src.domain.ports.repository import IConnectionRepository
from src.infrastructure.persistence.postgres.models.connection_orm import ConnectionORM


class SqlAlchemyConnectionRepository(IConnectionRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self.seen: dict[uuid.UUID, DatabaseConnection] = {}

    def _track(self, conn: DatabaseConnection) -> DatabaseConnection:
        existing = self.seen.get(conn.id)
        if existing is not None:
            return existing
        self.seen[conn.id] = conn
        return conn

    async def get(self, connection_id: uuid.UUID) -> DatabaseConnection | None:
        existing = self.seen.get(connection_id)
        if existing is not None:
            return existing
        result = await self._session.execute(
            select(ConnectionORM).where(ConnectionORM.id == connection_id)
        )
        orm = result.scalar_one_or_none()
        if orm is None:
            return None
        return self._track(self._to_domain(orm))

    async def list_by_owner(self, owner_id: uuid.UUID) -> list[DatabaseConnection]:
        result = await self._session.execute(
            select(ConnectionORM)
            .where(ConnectionORM.owner_id == owner_id)
            .order_by(ConnectionORM.created_at.desc())
        )
        return [self._to_domain(orm) for orm in result.scalars().all()]

    async def add(self, conn: DatabaseConnection) -> None:
        self.seen[conn.id] = conn
        self._session.add(self._to_orm(conn))

    async def update(self, conn: DatabaseConnection) -> None:
        self.seen[conn.id] = conn
        orm = await self._session.get(ConnectionORM, conn.id)
        if orm is None:
            raise ValueError(f"Connection {conn.id} not found")
        orm.name = conn.name
        orm.schema_cache = conn.schema_cache
        orm.is_active = conn.is_active

    @staticmethod
    def _to_domain(orm: ConnectionORM) -> DatabaseConnection:
        return DatabaseConnection(
            id=orm.id,
            owner_id=orm.owner_id,
            name=orm.name,
            engine=orm.engine,
            dsn=orm.dsn,
            schema_cache=orm.schema_cache,
            is_active=orm.is_active,
        )

    @staticmethod
    def _to_orm(conn: DatabaseConnection) -> ConnectionORM:
        return ConnectionORM(
            id=conn.id,
            owner_id=conn.owner_id,
            name=conn.name,
            engine=conn.engine,
            dsn=conn.dsn,
            schema_cache=conn.schema_cache,
            is_active=conn.is_active,
        )
