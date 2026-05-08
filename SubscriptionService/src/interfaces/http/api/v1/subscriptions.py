from typing import Annotated

from fastapi import APIRouter, Query, Request
from src.application.dto import (
    CreateCheckoutSessionDTO,
    CreateSubscriptionDTO,
    GetSubscriptionDTO,
    HandleWebhookDTO,
)
from src.domain.exceptions import PaymentProviderError, SecurityValidationError
from src.domain.models import Subscription
from src.interfaces.http.dependencies import SubscriptionServiceDep
from src.interfaces.http.schemas import (
    CreateCheckoutSessionRequest,
    CreateSubscriptionRequest,
    GetSubscriptionRequest,
    SubscriptionResponse,
)

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


def _to_subscription_response(subscription: Subscription) -> SubscriptionResponse:
    return SubscriptionResponse(
        subscription_id=subscription.id,
        subscription_type=subscription.type,
        email=subscription.email,
        is_active=subscription.is_active,
    )


@router.get("", response_model=SubscriptionResponse, status_code=200)
async def get_subscription(
    request: Annotated[GetSubscriptionRequest, Query()],
    subscription_service: SubscriptionServiceDep,
) -> SubscriptionResponse:
    subscription = await subscription_service.get_subscription(
        GetSubscriptionDTO(id=request.subscription_id)
    )
    return _to_subscription_response(subscription)


@router.post("", response_model=SubscriptionResponse, status_code=201)
async def create_subscription(
    request: CreateSubscriptionRequest,
    subscription_service: SubscriptionServiceDep,
) -> SubscriptionResponse:
    subscription = await subscription_service.create_subscription(
        CreateSubscriptionDTO(
            subscription_type=request.subscription_type,
            email=request.email,
        )
    )
    return _to_subscription_response(subscription)


@router.get("/checkout-session")
async def get_checkout_session(
    request: CreateCheckoutSessionRequest,
    subscription_service: SubscriptionServiceDep,
) -> dict[str, str]:
    result = await subscription_service.create_checkout_session(
        CreateCheckoutSessionDTO(
            subscription_id=request.subscription_id,
            price_id=request.price_id,
        )
    )
    return {"checkout_url": result.url}


@router.post("/webhook", status_code=200)
async def stripe_webhook(
    request: Request,
    subscription_service: SubscriptionServiceDep,
) -> dict[str, str]:
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if sig_header is None:
        raise PaymentProviderError

    try:
        await subscription_service.handle_webhook(
            HandleWebhookDTO(payload=payload, sig_header=sig_header)
        )
    except SecurityValidationError:
        raise SecurityValidationError
    except PaymentProviderError:
        raise PaymentProviderError

    return {"status": "success"}
