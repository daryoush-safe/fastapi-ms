from abc import ABC, abstractmethod


class IConnectionVerifier(ABC):
    @abstractmethod
    async def verify(self, engine: str, dsn: str) -> None: ...
