from __future__ import annotations

import logging

from src.application.dto import ActivateSubscriptionByEmailDTO
from src.domain.ports.unit_of_work import AbstractUnitOfWork

logger = logging.getLogger(__name__)


class ActivateSubscriptionByEmailUseCase:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, dto: ActivateSubscriptionByEmailDTO) -> None:
        async with self._uow as uow:
            sub = await uow.subscription.get_by_email(dto.email)
            if sub is None:
                logger.warning(
                    "ActivateSubscriptionByEmail: no subscription for email=%s",
                    dto.email,
                )
                return
            sub.activate(sub.type)
            await uow.subscription.update(sub)
