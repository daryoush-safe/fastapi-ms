import uuid
from abc import ABC, abstractmethod

from src.domain.models import QueryResult


class IQueryExecutor(ABC):
    @abstractmethod
    async def execute(
        self, dsn: str, sql: str, connection_id: uuid.UUID, prompt: str
    ) -> QueryResult: ...
