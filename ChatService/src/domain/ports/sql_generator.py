from abc import ABC, abstractmethod
from collections.abc import AsyncIterator


class ISqlGenerator(ABC):
    @abstractmethod
    def stream(self, question: str, schema: str) -> AsyncIterator[dict]: ...
