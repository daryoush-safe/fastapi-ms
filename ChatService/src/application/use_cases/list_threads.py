from src.application.dto import ListThreadsDTO, ThreadDTO
from src.domain.ports.unit_of_work import IUnitOfWork


class ListThreads:
    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, dto: ListThreadsDTO) -> list[ThreadDTO]:
        async with self._uow as uow:
            threads = await uow.threads.list_by_user(dto.user_id)
        return [ThreadDTO.from_domain(thread) for thread in threads]
