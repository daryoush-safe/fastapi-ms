from collections.abc import AsyncIterator, Callable

from src.application.dto import (
    CreateThreadDTO,
    GetMessagesDTO,
    ListThreadsDTO,
    MessageDTO,
    SendMessageDTO,
    ThreadDTO,
    UpsertConnectionDTO,
)
from src.application.use_cases.create_thread import CreateThread
from src.application.use_cases.get_thread_messages import GetThreadMessages
from src.application.use_cases.list_threads import ListThreads
from src.application.use_cases.send_message import SendMessage
from src.application.use_cases.upsert_connection import UpsertConnection
from src.domain.ports.connection_validator import IConnectionValidator
from src.domain.ports.sql_generator import ISqlGenerator
from src.domain.ports.unit_of_work import IUnitOfWork


class ChatService:
    def __init__(
        self,
        uow_factory: Callable[[], IUnitOfWork],
        sql_generator: ISqlGenerator,
        connection_validator: IConnectionValidator,
    ) -> None:
        self._uow_factory = uow_factory
        self._sql_generator = sql_generator
        self._connection_validator = connection_validator

    async def create_thread(self, dto: CreateThreadDTO, access_token: str) -> ThreadDTO:
        return await CreateThread(self._uow_factory(), self._connection_validator).execute(
            dto, access_token
        )

    async def list_threads(self, dto: ListThreadsDTO) -> list[ThreadDTO]:
        return await ListThreads(self._uow_factory()).execute(dto)

    async def get_thread_messages(self, dto: GetMessagesDTO) -> list[MessageDTO]:
        return await GetThreadMessages(self._uow_factory()).execute(dto)

    async def send_message(self, dto: SendMessageDTO) -> AsyncIterator[str]:
        return await SendMessage(self._uow_factory(), self._sql_generator).execute(dto)

    async def upsert_connection(self, dto: UpsertConnectionDTO) -> None:
        return await UpsertConnection(self._uow_factory()).execute(dto)
