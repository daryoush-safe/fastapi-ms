from typing import Annotated

from fastapi import Depends
from src.application.services import SubscriptionService
from src.container import Container


def get_subscription_service() -> SubscriptionService:
    return Container.subscription_service()


SubscriptionServiceDep = Annotated[
    SubscriptionService, Depends(get_subscription_service)
]
