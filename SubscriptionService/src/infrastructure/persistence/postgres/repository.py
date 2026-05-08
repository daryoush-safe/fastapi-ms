from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.exceptions import SubscriptionNotFoundError
from src.domain.models import Subscription
from src.domain.ports.repository import AbstractSubscriptionRepository
from src.infrastructure.persistence.postgres.models.subscription_orm import (
    SubscriptionORM,
)


class SqlAlchemySubscriptionRepository(AbstractSubscriptionRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self.seen: set[Subscription] = set()

    async def get_by_id(self, subscription_id: UUID) -> Subscription | None:
        result = await self._session.execute(
            select(SubscriptionORM).where(SubscriptionORM.id == subscription_id)
        )
        orm = result.scalar_one_or_none()
        if orm is None:
            return None
        sub = self._to_domain(orm)
        self.seen.add(sub)
        return sub

    async def get_by_email(self, email: str) -> Subscription | None:
        result = await self._session.execute(
            select(SubscriptionORM).where(SubscriptionORM.email == email)
        )
        orm = result.scalar_one_or_none()
        if orm is None:
            return None
        sub = self._to_domain(orm)
        self.seen.add(sub)
        return sub

    async def add(self, subscription: Subscription) -> None:
        self.seen.add(subscription)
        self._session.add(self._to_orm(subscription))

    async def update(self, subscription: Subscription) -> None:
        self.seen.add(subscription)
        orm = await self._session.get(SubscriptionORM, subscription.id)
        if orm is None:
            raise SubscriptionNotFoundError(subscription.id)
        orm.subscription_type = subscription.type
        orm.email = subscription.email
        orm.is_active = subscription.is_active

    async def delete(self, subscription: Subscription) -> None:
        orm = await self._session.get(SubscriptionORM, subscription.id)
        if orm:
            await self._session.delete(orm)

    @staticmethod
    def _to_domain(orm: SubscriptionORM) -> Subscription:
        return Subscription(
            id=orm.id,
            type=orm.subscription_type,
            email=orm.email,
            is_active=orm.is_active,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )

    @staticmethod
    def _to_orm(subscription: Subscription) -> SubscriptionORM:
        return SubscriptionORM(
            id=subscription.id,
            email=subscription.email,
            subscription_type=subscription.type,
            is_active=subscription.is_active,
        )
