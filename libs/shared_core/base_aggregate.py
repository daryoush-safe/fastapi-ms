from __future__ import annotations

from dataclasses import dataclass, field

from libs.shared_core.base_event import DomainEvent


@dataclass
class AggregateRoot:
    _domain_events: list[DomainEvent] = field(
        default_factory=list, init=False, repr=False, compare=False, hash=False
    )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return getattr(self, "id", None) == getattr(other, "id", None)

    def __hash__(self) -> int:
        return hash(getattr(self, "id", id(self)))

    def record_event(self, event: DomainEvent) -> None:
        self._domain_events.append(event)

    def pull_events(self) -> list[DomainEvent]:
        events, self._domain_events = self._domain_events, []
        return events
