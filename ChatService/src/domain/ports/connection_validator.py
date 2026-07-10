import uuid
from abc import ABC, abstractmethod


class IConnectionValidator(ABC):
    @abstractmethod
    async def validate(self, connection_id: uuid.UUID, access_token: str) -> None: ...
