from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CheckoutSession:
    url: str
    session_id: str


@dataclass(frozen=True)
class WebhookEvent:
    event_type: str
    data: dict[str, Any]


class AbstractPaymentClient(ABC):
    @abstractmethod
    async def create_checkout_session(
        self,
        email: str,
        price_id: str,
    ) -> CheckoutSession: ...

    @abstractmethod
    async def verify_webhook(
        self,
        payload: bytes,
        sig_header: str,
    ) -> WebhookEvent: ...
