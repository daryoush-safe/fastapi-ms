from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Subscription:
    id: uuid.UUID
    type: str | None
    email: str
    is_active: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create(cls, type: str, email: str) -> Subscription:
        return cls(
            id=uuid.uuid4(),
            type=type,
            email=email,
        )

    def activate(self, subscription_type: str | None) -> None:
        self.is_active = True
        self.type = subscription_type

    def deactivate(self) -> None:
        self.is_active = False
