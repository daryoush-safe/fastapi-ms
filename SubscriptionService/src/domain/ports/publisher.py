from abc import ABC, abstractmethod

from libs.shared_core.base_event import DomainEvent


class AbstractEventPublisher(ABC):
    @abstractmethod
    async def publish(self, event: DomainEvent) -> None: ...
