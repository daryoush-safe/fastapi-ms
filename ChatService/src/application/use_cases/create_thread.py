import uuid

from src.application.dto import CreateThreadDTO, ThreadDTO
from src.domain.models import ChatThread
from src.domain.ports.connection_validator import IConnectionValidator
from src.domain.ports.unit_of_work import IUnitOfWork


class CreateThread:
    def __init__(self, uow: IUnitOfWork, validator: IConnectionValidator) -> None:
        self._uow = uow
        self._validator = validator

    async def execute(self, dto: CreateThreadDTO, access_token: str) -> ThreadDTO:
        await self._validator.validate(dto.connection_id, access_token)

        thread = ChatThread(
            id=uuid.uuid4(),
            user_id=dto.user_id,
            connection_id=dto.connection_id,
            title=(dto.title.strip() or None) if dto.title else None,
        )
        async with self._uow as uow:
            await uow.threads.add(thread)
        return ThreadDTO.from_domain(thread)
