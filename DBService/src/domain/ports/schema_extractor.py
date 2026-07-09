import uuid
from abc import ABC, abstractmethod

from src.domain.models import DatabaseSchema


class ISchemaExtractor(ABC):
    @abstractmethod
    async def execute(
        self, engine: str, dsn: str, connection_id: uuid.UUID
    ) -> DatabaseSchema: ...
