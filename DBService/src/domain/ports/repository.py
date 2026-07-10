import uuid
from abc import ABC, abstractmethod

from src.domain.models import DatabaseConnection


class IConnectionRepository(ABC):
    @abstractmethod
    async def get(self, connection_id: uuid.UUID) -> DatabaseConnection | None: ...
    @abstractmethod
    async def list_by_owner(self, owner_id: uuid.UUID) -> list[DatabaseConnection]: ...
    @abstractmethod
    async def add(self, conn: DatabaseConnection) -> None: ...
    @abstractmethod
    async def update(self, conn: DatabaseConnection) -> None: ...
