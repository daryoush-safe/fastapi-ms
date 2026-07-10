from datetime import datetime, timezone

from src.application.dto import UpsertConnectionDTO
from src.domain.models import ConnectionRef
from src.domain.ports.unit_of_work import IUnitOfWork


class UpsertConnection:
    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, dto: UpsertConnectionDTO) -> None:
        async with self._uow as uow:
            ref = await uow.connections.get(dto.connection_id)
            if ref is None:
                ref = ConnectionRef(
                    connection_id=dto.connection_id,
                    owner_id=dto.owner_id,
                )
            ref.owner_id = dto.owner_id
            if dto.title is not None:
                ref.title = dto.title
            if dto.engine is not None:
                ref.engine = dto.engine
            if dto.schema is not None:
                ref.schema = dto.schema
            ref.updated_at = datetime.now(timezone.utc)
            await uow.connections.upsert(ref)
