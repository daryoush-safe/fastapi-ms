from __future__ import annotations

from src.application.dto import GetConnectionDTO
from src.domain.exceptions import ConnectionAccessDenied, ConnectionNotFound
from src.domain.models import DatabaseConnection
from src.domain.ports.unit_of_work import IUnitOfWork


class GetConnection:
    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, dto: GetConnectionDTO) -> DatabaseConnection:
        async with self._uow as uow:
            conn = await uow.connections.get(dto.connection_id)
            if conn is None:
                raise ConnectionNotFound(dto.connection_id)
            if conn.owner_id != dto.owner_id:
                raise ConnectionAccessDenied(dto.connection_id)
            return conn
