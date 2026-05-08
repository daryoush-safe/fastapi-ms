from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime

from src.domain.events import UserCreated, UserEmailChanged, UserProfileUpdated

from libs.shared_core.base_aggregate import AggregateRoot


@dataclass
class User(AggregateRoot):
    id: uuid.UUID
    username: str
    email: str
    hashed_password: str
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create(cls, username: str, email: str, hashed_password: str) -> User:
        user = cls(
            id=uuid.uuid4(),
            username=username,
            email=email,
            hashed_password=hashed_password,
        )
        user.record_event(
            UserCreated(user_id=user.id, email=user.email, username=user.username)
        )
        return user

    def change_email(self, new_email: str) -> None:
        old = self.email
        self.email = new_email
        self.record_event(
            UserEmailChanged(user_id=self.id, old_email=old, new_email=new_email)
        )

    def update_profile(self, username: str) -> None:
        self.username = username
        self.record_event(UserProfileUpdated(user_id=self.id, username=username))
