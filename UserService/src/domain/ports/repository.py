from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.models import User


class AbstractUserRepository(ABC):
    seen: set[User]

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> User | None: ...

    @abstractmethod
    async def exists_by_email(self, email: str) -> bool: ...

    @abstractmethod
    async def add(self, user: User) -> None: ...

    @abstractmethod
    async def update(self, user: User) -> None: ...

    @abstractmethod
    async def delete(self, user: User) -> None: ...
