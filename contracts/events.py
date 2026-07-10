from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

# ─── User Service events ──────────────────────────────────────────────────────


@dataclass(frozen=True)
class UserCreated:
    user_id: uuid.UUID
    email: str
    username: str
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    event_type: str = field(default="UserCreated", init=False)


@dataclass(frozen=True)
class UserEmailChanged:
    user_id: uuid.UUID
    old_email: str
    new_email: str
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    event_type: str = field(default="UserEmailChanged", init=False)


@dataclass(frozen=True)
class UserProfileUpdated:
    user_id: uuid.UUID
    username: str
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    event_type: str = field(default="UserProfileUpdated", init=False)


# ─── Subscription Service events ─────────────────────────────────────────────


@dataclass(frozen=True)
class SubscriptionCreated:
    subscription_id: uuid.UUID
    email: str
    subscription_type: str | None
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    event_type: str = field(default="SubscriptionCreated", init=False)


@dataclass(frozen=True)
class SubscriptionActivated:
    subscription_id: uuid.UUID
    email: str
    subscription_type: str | None
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    event_type: str = field(default="SubscriptionActivated", init=False)


@dataclass(frozen=True)
class SubscriptionDeactivated:
    subscription_id: uuid.UUID
    email: str
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    event_type: str = field(default="SubscriptionDeactivated", init=False)


# ─── DB Service events ───────────────────────────────────────────────────────
# Emitted from DBService's outbox (aggregate_type "dbconnection") and consumed by
# ChatService to maintain a local replica of connections + their extracted schema.


@dataclass(frozen=True)
class DatabaseConnectionRegistered:
    connection_id: uuid.UUID
    owner_id: uuid.UUID
    name: str
    engine: str
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    event_type: str = field(default="DatabaseConnectionRegistered", init=False)


@dataclass(frozen=True)
class ConnectionSchemaExtracted:
    connection_id: uuid.UUID
    owner_id: uuid.UUID
    schema: str  # rendered schema text, forwarded verbatim to the ML service
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    event_type: str = field(default="ConnectionSchemaExtracted", init=False)
