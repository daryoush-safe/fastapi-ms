import uuid
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator


class ISqlGenerator(ABC):
    @abstractmethod
    def stream(
        self,
        question: str,
        schema: str,
        *,
        db_id: uuid.UUID,
        thread_id: uuid.UUID,
        access_token: str,
    ) -> AsyncIterator[dict]: ...
