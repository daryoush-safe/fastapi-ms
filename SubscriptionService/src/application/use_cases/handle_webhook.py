import logging

from src.application.dto import HandleWebhookDTO
from src.domain.exceptions import SubscriptionNotFoundError
from src.domain.ports.payment import AbstractPaymentClient
from src.domain.ports.unit_of_work import AbstractUnitOfWork

logger = logging.getLogger(__name__)

CHECKOUT_SESSION_COMPLETED = "checkout.session.completed"
SUBSCRIPTION_DELETED = "customer.subscription.deleted"


class HandleWebhookUseCase:
    def __init__(
        self,
        uow: AbstractUnitOfWork,
        payment: AbstractPaymentClient,
    ) -> None:
        self._uow = uow
        self._payment = payment

    async def execute(self, dto: HandleWebhookDTO) -> None:
        event = await self._payment.verify_webhook(
            payload=dto.payload,
            sig_header=dto.sig_header,
        )

        if event.event_type == CHECKOUT_SESSION_COMPLETED:
            await self._handle_checkout_completed(event.data)

        elif event.event_type == SUBSCRIPTION_DELETED:
            await self._handle_subscription_deleted(event.data)

        else:
            logger.info(
                "Unhandled Stripe event", extra={"event_type": event.event_type}
            )

    async def _handle_checkout_completed(self, data: dict) -> None:
        email: str | None = (data.get("customer_details") or {}).get("email")
        subscription_type: str | None = data.get("metadata", {}).get(
            "subscription_type", "premium"
        )

        if email is None:
            logger.warning("checkout.session.completed received with no customer email")
            return

        async with self._uow as uow:
            subscription = await uow.subscription.get_by_email(email)
            if subscription is None:
                raise SubscriptionNotFoundError(email)

            subscription.activate(subscription_type=subscription_type)
            await uow.subscription.update(subscription)

        logger.info("Subscription activated", extra={"email": email})

    async def _handle_subscription_deleted(self, data: dict) -> None:
        email: str | None = (data.get("customer_details") or {}).get("email")

        if email is None:
            logger.warning(
                "customer.subscription.deleted received with no customer email"
            )
            return

        async with self._uow as uow:
            subscription = await uow.subscription.get_by_email(email)
            if subscription is None:
                raise SubscriptionNotFoundError(email)

            subscription.deactivate()
            await uow.subscription.update(subscription)

        logger.info("Subscription deactivated", extra={"email": email})
