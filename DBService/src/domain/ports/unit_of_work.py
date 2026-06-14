from abc import ABC, abstractmethod
from typing_extensions import Self
from DBService.src.domain.ports import repository


class IUnitOfWork(ABC):
    connections: repository.IConnectionRepository

    @abstractmethod
    async def __aenter__(self) -> Self: ...
    @abstractmethod
    async def __aexit__(self, exc_type, exc, tb) -> None: ...
    @abstractmethod
    async def commit(self) -> None: ...
    @abstractmethod
    async def rollback(self) -> None: ...