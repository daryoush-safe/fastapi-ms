from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from src.domain.ports.unit_of_work import AbstractUnitOfWork
from src.infrastructure.persistence.postgres.repository import (
    SqlAlchemySubscriptionRepository,
)


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def __aenter__(self) -> Self:
        self._session = self._session_factory()
        self.subscription = SqlAlchemySubscriptionRepository(self._session)
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        try:
            if exc_type:
                await self.rollback()
            else:
                await self.commit()
        finally:
            await self._session.close()

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()
