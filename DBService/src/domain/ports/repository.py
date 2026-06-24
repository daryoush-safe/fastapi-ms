import uuid
from abc import ABC, abstractmethod

from src.domain.models import DatabaseConnection


class IConnectionRepository(ABC):
    @abstractmethod
    async def get(self, connection_id: uuid.UUID) -> DatabaseConnection | None: ...
    @abstractmethod
    async def add(self, conn: DatabaseConnection) -> None: ...
