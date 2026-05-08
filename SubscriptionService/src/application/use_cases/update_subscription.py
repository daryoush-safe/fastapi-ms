from __future__ import annotations

import logging

from src.application.dto import UpdateSubscriptionEmailDTO
from src.domain.ports.unit_of_work import AbstractUnitOfWork

logger = logging.getLogger(__name__)


class UpdateSubscriptionEmailUseCase:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, dto: UpdateSubscriptionEmailDTO) -> None:
        async with self._uow as uow:
            sub = await uow.subscription.get_by_email(dto.old_email)
            if sub is None:
                logger.warning(
                    "UpdateSubscriptionEmail: no subscription for old_email=%s",
                    dto.old_email,
                )
                return
            sub.email = dto.new_email
            await uow.subscription.update(sub)
