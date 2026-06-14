from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from DBService.src.domain.models import DatabaseConnection
from DBService.src.domain.ports.repository import IConnectionRepository
from DBService.src.infrastructure.persistence.postgres.models.connection_orm import ConnectionORM


class SqlAlchemyConnectionRepository(IConnectionRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, connection_id: uuid.UUID) -> DatabaseConnection | None:
        result = await self._session.execute(
            select(ConnectionORM).where(ConnectionORM.id == connection_id)
        )
        orm = result.scalar_one_or_none()
        if orm is None:
            return None
        return self._to_domain(orm)

    async def add(self, conn: DatabaseConnection) -> None:
        self._session.add(self._to_orm(conn))

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
