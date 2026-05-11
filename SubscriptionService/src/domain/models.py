from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

from src.domain.events import (
    SubscriptionActivated,
    SubscriptionCreated,
    SubscriptionDeactivated,
)

from libs.shared_core.base_aggregate import AggregateRoot


@dataclass(eq=False)
class Subscription(AggregateRoot):
    id: uuid.UUID
    type: str | None
    email: str
    is_active: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(cls, type: str, email: str) -> Subscription:
        sub = cls(id=uuid.uuid4(), type=type, email=email)
        sub.record_event(
            SubscriptionCreated(
                subscription_id=sub.id,
                email=sub.email,
                subscription_type=sub.type,
            )
        )
        return sub

    def activate(self, subscription_type: str | None) -> None:
        self.is_active = True
        self.type = subscription_type
        self.record_event(
            SubscriptionActivated(
                subscription_id=self.id,
                email=self.email,
                subscription_type=self.type,
            )
        )

    def deactivate(self) -> None:
        self.is_active = False
        self.record_event(
            SubscriptionDeactivated(subscription_id=self.id, email=self.email)
        )
