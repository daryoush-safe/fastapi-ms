from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class User:
    id: uuid.UUID
    username: str
    email: str
    hashed_password: str
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create(cls, username: str, email: str, hashed_password: str) -> User:
        return cls(
            id=uuid.uuid4(),
            username=username,
            email=email,
            hashed_password=hashed_password,
        )
