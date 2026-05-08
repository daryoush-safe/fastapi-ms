from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.models import Subscription


class AbstractSubscriptionRepository(ABC):
    @abstractmethod
    async def get_by_id(self, subscription_id: UUID) -> Subscription | None: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> Subscription | None: ...

    @abstractmethod
    async def add(self, subscription: Subscription) -> None: ...

    @abstractmethod
    async def update(self, subscription: Subscription) -> None: ...

    @abstractmethod
    async def delete(self, subscription: Subscription) -> None: ...
