from __future__ import annotations

from src.application.dto import ListConnectionsDTO
from src.domain.models import DatabaseConnection
from src.domain.ports.unit_of_work import IUnitOfWork


class ListConnections:
    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, dto: ListConnectionsDTO) -> list[DatabaseConnection]:
        async with self._uow as uow:
            return await uow.connections.list_by_owner(dto.owner_id)
