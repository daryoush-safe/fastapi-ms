from __future__ import annotations

from dataclasses import dataclass, field

from libs.shared_core.base_event import DomainEvent


@dataclass
class AggregateRoot:
    _domain_events: list[DomainEvent] = field(
        default_factory=list, init=False, repr=False, compare=False
    )

    def record_event(self, event: DomainEvent) -> None:
        self._domain_events.append(event)

    def pull_events(self) -> list[DomainEvent]:
        events, self._domain_events = self._domain_events, []
        return events
