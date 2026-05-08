from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class GetSubscriptionDTO:
    id: UUID


@dataclass(frozen=True)
class CreateSubscriptionDTO:
    subscription_type: str
    email: str


@dataclass(frozen=True)
class CreateCheckoutSessionDTO:
    subscription_id: UUID
    price_id: str


@dataclass(frozen=True)
class HandleWebhookDTO:
    payload: bytes
    sig_header: str
