from src.application.dto import GetMessagesDTO, MessageDTO
from src.domain.exceptions import ThreadAccessDenied, ThreadNotFound
from src.domain.ports.unit_of_work import IUnitOfWork


class GetThreadMessages:
    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, dto: GetMessagesDTO) -> list[MessageDTO]:
        async with self._uow as uow:
            thread = await uow.threads.get(dto.thread_id)
            if thread is None:
                raise ThreadNotFound(dto.thread_id)
            if thread.user_id != dto.user_id:
                raise ThreadAccessDenied(dto.thread_id)
            messages = await uow.messages.list_by_thread(dto.thread_id)
        return [MessageDTO.from_domain(message) for message in messages]
