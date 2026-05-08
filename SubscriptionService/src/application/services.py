from src.application.dto import (
    CreateCheckoutSessionDTO,
    CreateSubscriptionDTO,
    GetSubscriptionDTO,
    HandleWebhookDTO,
)
from src.application.use_cases.create_checkout_session import (
    CreateCheckoutSessionUseCase,
)
from src.application.use_cases.create_subscription import CreateSubscriptionUseCase
from src.application.use_cases.get_subscription import GetSubscriptionUseCase
from src.application.use_cases.handle_webhook import HandleWebhookUseCase
from src.domain.models import Subscription
from src.domain.ports.payment import AbstractPaymentClient, CheckoutSession
from src.domain.ports.unit_of_work import AbstractUnitOfWork


class SubscriptionService:
    def __init__(self, uow: AbstractUnitOfWork, payment: AbstractPaymentClient) -> None:
        self._uow = uow
        self._payment = payment

    async def get_subscription(self, dto: GetSubscriptionDTO) -> Subscription:
        return await GetSubscriptionUseCase(self._uow).execute(dto)

    async def create_subscription(self, dto: CreateSubscriptionDTO) -> Subscription:
        return await CreateSubscriptionUseCase(self._uow).execute(dto)

    async def create_checkout_session(
        self, dto: CreateCheckoutSessionDTO
    ) -> CheckoutSession:
        return await CreateCheckoutSessionUseCase(self._uow, self._payment).execute(dto)

    async def handle_webhook(self, dto: HandleWebhookDTO) -> None:
        await HandleWebhookUseCase(self._uow, self._payment).execute(dto)
