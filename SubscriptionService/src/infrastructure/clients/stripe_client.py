import stripe
from src.config import get_settings
from src.domain.exceptions import PaymentProviderError, SecurityValidationError
from src.domain.ports.payment import (
    AbstractPaymentClient,
    CheckoutSession,
    WebhookEvent,
)


class StripeClient(AbstractPaymentClient):
    def __init__(self) -> None:
        stripe.api_key = get_settings().stripe_secret_key

    async def create_checkout_session(
        self,
        email: str,
        price_id: str,
    ) -> CheckoutSession:
        try:
            session = stripe.checkout.Session.create(
                customer_email=email,
                success_url=get_settings().stripe_success_url,
                cancel_url=get_settings().stripe_cancel_url,
                line_items=[{"price": price_id, "quantity": 1}],
                mode="subscription",
                billing_address_collection="required",
            )
        except stripe.StripeError:
            raise PaymentProviderError

        if session.url is None:
            raise PaymentProviderError

        return CheckoutSession(
            url=session.url,
            session_id=session.id,
        )

    async def verify_webhook(
        self,
        payload: bytes,
        sig_header: str,
    ) -> WebhookEvent:
        try:
            event = stripe.Webhook.construct_event(
                payload,
                sig_header,
                get_settings().stripe_webhook_secret,
            )
        except stripe.SignatureVerificationError:
            raise SecurityValidationError
        except stripe.StripeError:
            raise PaymentProviderError

        return WebhookEvent(
            event_type=event["type"],
            data=event["data"]["object"],
        )
