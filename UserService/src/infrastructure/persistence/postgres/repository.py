from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.models import User
from src.domain.ports.repository import AbstractUserRepository
from src.infrastructure.persistence.postgres.models.user_orm import UserORM


class SqlAlchemyUserRepository(AbstractUserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_email(self, email: str) -> User | None:
        result = await self._session.execute(
            select(UserORM).where(UserORM.email == email)
        )
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def get_by_id(self, user_id: UUID) -> User | None:
        result = await self._session.execute(
            select(UserORM).where(UserORM.id == user_id)
        )
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def exists_by_email(self, email: str) -> bool:
        result = await self._session.execute(
            select(UserORM.id).where(UserORM.email == email)
        )
        return result.scalar_one_or_none() is not None

    async def add(self, user: User) -> None:
        self._session.add(self._to_orm(user))

    async def update(self, user: User) -> None:
        orm = await self._session.get(UserORM, user.id)
        if orm is None:
            raise ValueError(f"User {user.id} not found")
        orm.username = user.username
        orm.email = user.email
        orm.hashed_password = user.hashed_password
        orm.is_active = user.is_active

    async def delete(self, user: User) -> None:
        orm = await self._session.get(UserORM, user.id)
        if orm:
            await self._session.delete(orm)

    @staticmethod
    def _to_domain(orm: UserORM) -> User:
        return User(
            id=orm.id,
            username=orm.username,
            email=orm.email,
            hashed_password=orm.hashed_password,
            is_active=orm.is_active,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )

    @staticmethod
    def _to_orm(user: User) -> UserORM:
        return UserORM(
            id=user.id,
            username=user.username,
            email=user.email,
            hashed_password=user.hashed_password,
            is_active=user.is_active,
        )
