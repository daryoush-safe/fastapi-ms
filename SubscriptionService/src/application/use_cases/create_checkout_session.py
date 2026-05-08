from src.application.dto import CreateCheckoutSessionDTO
from src.domain.exceptions import SubscriptionNotFoundError
from src.domain.ports.payment import AbstractPaymentClient, CheckoutSession
from src.domain.ports.unit_of_work import AbstractUnitOfWork


class CreateCheckoutSessionUseCase:
    def __init__(self, uow: AbstractUnitOfWork, payment: AbstractPaymentClient) -> None:
        self._uow = uow
        self._payment = payment

    async def execute(self, dto: CreateCheckoutSessionDTO) -> CheckoutSession:
        async with self._uow as uow:
            subscription = await uow.subscription.get_by_id(dto.subscription_id)
            if subscription is None:
                raise SubscriptionNotFoundError(dto.subscription_id)
            return await self._payment.create_checkout_session(
                email=subscription.email,
                price_id=dto.price_id,
            )
