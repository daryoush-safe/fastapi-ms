from abc import ABC, abstractmethod
from typing import Self

from src.domain.ports.repository import AbstractUserRepository


class AbstractUnitOfWork(ABC):
    users: AbstractUserRepository

    @abstractmethod
    async def __aenter__(self) -> Self: ...

    @abstractmethod
    async def __aexit__(self, exc_type, exc, tb) -> None: ...

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...
