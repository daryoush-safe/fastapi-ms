from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from libs.shared_core.base_event import DomainEvent


@dataclass(frozen=True)
class UserCreated(DomainEvent):
    user_id: uuid.UUID = field(default_factory=uuid.uuid4)
    email: str = ""
    username: str = ""


@dataclass(frozen=True)
class UserEmailChanged(DomainEvent):
    user_id: uuid.UUID = field(default_factory=uuid.uuid4)
    old_email: str = ""
    new_email: str = ""


@dataclass(frozen=True)
class UserProfileUpdated(DomainEvent):
    user_id: uuid.UUID = field(default_factory=uuid.uuid4)
    username: str = ""
