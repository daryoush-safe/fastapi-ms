import uuid
from abc import ABC, abstractmethod

from src.domain.models import ChatMessage, ChatThread, ConnectionRef


class IChatThreadRepository(ABC):
    @abstractmethod
    async def get(self, thread_id: uuid.UUID) -> ChatThread | None: ...
    @abstractmethod
    async def list_by_user(self, user_id: uuid.UUID) -> list[ChatThread]: ...
    @abstractmethod
    async def add(self, thread: ChatThread) -> None: ...
    @abstractmethod
    async def update(self, thread: ChatThread) -> None: ...


class IChatMessageRepository(ABC):
    @abstractmethod
    async def add(self, message: ChatMessage) -> None: ...
    @abstractmethod
    async def list_by_thread(self, thread_id: uuid.UUID) -> list[ChatMessage]: ...


class IConnectionRefRepository(ABC):
    @abstractmethod
    async def get(self, connection_id: uuid.UUID) -> ConnectionRef | None: ...
    @abstractmethod
    async def upsert(self, ref: ConnectionRef) -> None: ...
