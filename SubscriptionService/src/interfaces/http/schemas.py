from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class GetSubscriptionRequest(BaseModel):
    subscription_id: UUID


class CreateSubscriptionRequest(BaseModel):
    subscription_type: str
    email: str


class CreateCheckoutSessionRequest(BaseModel):
    subscription_id: UUID
    price_id: str


class SubscriptionResponse(BaseModel):
    subscription_id: UUID
    subscription_type: Optional[str] = None
    email: str
    is_active: bool
