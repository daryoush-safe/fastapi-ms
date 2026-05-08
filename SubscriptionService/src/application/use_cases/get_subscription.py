from src.application.dto import GetSubscriptionDTO
from src.domain.exceptions import SubscriptionNotFoundError
from src.domain.models import Subscription
from src.domain.ports.unit_of_work import AbstractUnitOfWork


class GetSubscriptionUseCase:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, dto: GetSubscriptionDTO) -> Subscription:
        async with self._uow as uow:
            subscription = await uow.subscription.get_by_id(dto.id)
            if subscription is None:
                raise SubscriptionNotFoundError(dto.id)
            return subscription
