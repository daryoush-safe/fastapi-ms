import uuid

from src.application.dto import CreateThreadDTO, ThreadDTO
from src.domain.models import ChatThread
from src.domain.ports.unit_of_work import IUnitOfWork


class CreateThread:
    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, dto: CreateThreadDTO) -> ThreadDTO:
        thread = ChatThread(
            id=uuid.uuid4(),
            user_id=dto.user_id,
            title=(dto.title.strip() or None) if dto.title else None,
        )
        async with self._uow as uow:
            await uow.threads.add(thread)
        return ThreadDTO.from_domain(thread)
