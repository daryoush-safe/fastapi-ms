from __future__ import annotations

import logging
import secrets
from typing import Any, Awaitable, Callable

from src.application.dto import CreateUserDTO
from src.application.services import UserService
from src.domain.exceptions import UserAlreadyExistsError

logger = logging.getLogger(__name__)

Handler = Callable[[dict[str, Any]], Awaitable[None]]


class UserServiceEventRegistry:
    def __init__(self, user_service: UserService) -> None:
        self._user_service = user_service
        self._handlers: dict[str, Handler] = {
            "SubscriptionCreated": self._on_subscription_created,
        }

    def get(self, event_type: str) -> Handler | None:
        return self._handlers.get(event_type)

    async def _on_subscription_created(self, payload: dict[str, Any]) -> None:
        logger.info("Handling SubscriptionCreated: %s", payload)
        temp_password = secrets.token_urlsafe(16)
        try:
            await self._user_service.create_user(
                CreateUserDTO(
                    email=payload["email"],
                    username=payload["email"].split("@")[0],
                    password=temp_password,
                )
            )
        except UserAlreadyExistsError:
            logger.info("User already exists for email=%s, skipping", payload["email"])
