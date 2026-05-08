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


@dataclass(frozen=True)
class ActivateSubscriptionByEmailDTO:
    email: str


@dataclass(frozen=True)
class UpdateSubscriptionEmailDTO:
    old_email: str
    new_email: str
