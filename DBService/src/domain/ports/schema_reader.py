from abc import ABC, abstractmethod

# from shared_core.base_event import DomainEvent


class ISchemaReader(ABC):
    @abstractmethod
    async def read_schema(self, dsn: str) -> dict: ...
