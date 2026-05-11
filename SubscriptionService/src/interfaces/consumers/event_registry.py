from __future__ import annotations

import logging
from typing import Any, Awaitable, Callable

from src.application.dto import (
    ActivateSubscriptionByEmailDTO,
    UpdateSubscriptionEmailDTO,
)
from src.application.services import SubscriptionService

logger = logging.getLogger(__name__)

Handler = Callable[[dict[str, Any]], Awaitable[None]]


class SubscriptionServiceEventRegistry:
    def __init__(self, subscription_service: SubscriptionService) -> None:
        self._subscription_service = subscription_service
        self._handlers: dict[str, Handler] = {
            "UserCreated": self._on_user_created,
            "UserEmailChanged": self._on_user_email_changed,
        }

    def get(self, event_type: str) -> Handler | None:
        return self._handlers.get(event_type)

    async def _on_user_created(self, payload: dict[str, Any]) -> None:
        logger.info("Handling UserCreated: %s", payload)
        await self._subscription_service.activate_subscription_by_email(
            ActivateSubscriptionByEmailDTO(email=payload["email"])
        )

    async def _on_user_email_changed(self, payload: dict[str, Any]) -> None:
        logger.info("Handling UserEmailChanged: %s", payload)
        await self._subscription_service.update_subscription_email(
            UpdateSubscriptionEmailDTO(
                old_email=payload["old_email"],
                new_email=payload["new_email"],
            )
        )
