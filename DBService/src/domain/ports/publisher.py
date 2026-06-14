from abc import ABC, abstractmethod
from shared_core.base_event import DomainEvent

class IEventPublisher(ABC):
    @abstractmethod
    async def publish(self, event: DomainEvent) -> None: ...
