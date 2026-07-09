from __future__ import annotations

from src.application.dto import ExtractSchemaDTO, SchemaResultDTO
from src.domain.exceptions import (
    ConnectionAccessDenied,
    ConnectionNotFound,
    SchemaExtractionError,
)
from src.domain.ports.schema_extractor import ISchemaExtractor
from src.domain.ports.unit_of_work import IUnitOfWork


class ExtractSchema:
    def __init__(self, uow: IUnitOfWork, schema_extractor: ISchemaExtractor) -> None:
        self._uow = uow
        self._schema_extractor = schema_extractor

    async def execute(self, dto: ExtractSchemaDTO) -> SchemaResultDTO:
        async with self._uow as uow:
            conn = await uow.connections.get(dto.connection_id)
            if conn is None:
                raise ConnectionNotFound(dto.connection_id)
            if conn.owner_id != dto.owner_id:
                raise ConnectionAccessDenied(dto.connection_id)
            engine, dsn = conn.engine, conn.dsn

        try:
            schema = await self._schema_extractor.execute(engine, dsn, dto.connection_id)
        except Exception as e:
            raise SchemaExtractionError(str(e)) from e

        return SchemaResultDTO.from_domain(schema)
