from src.application.dto import CreateSubscriptionDTO
from src.domain.models import Subscription
from src.domain.ports.unit_of_work import AbstractUnitOfWork


class CreateSubscriptionUseCase:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, dto: CreateSubscriptionDTO) -> Subscription:
        async with self._uow as uow:
            subscription = Subscription.create(
                type=dto.subscription_type,
                email=dto.email,
            )
            await uow.subscription.add(subscription)
            return subscription
