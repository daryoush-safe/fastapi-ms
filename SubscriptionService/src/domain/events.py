from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from libs.shared_core.base_event import DomainEvent


@dataclass(frozen=True)
class SubscriptionCreated(DomainEvent):
    subscription_id: uuid.UUID = field(default_factory=uuid.uuid4)
    email: str = ""
    subscription_type: str | None = None


@dataclass(frozen=True)
class SubscriptionActivated(DomainEvent):
    subscription_id: uuid.UUID = field(default_factory=uuid.uuid4)
    email: str = ""
    subscription_type: str | None = None


@dataclass(frozen=True)
class SubscriptionDeactivated(DomainEvent):
    subscription_id: uuid.UUID = field(default_factory=uuid.uuid4)
    email: str = ""
