import logging
from collections.abc import Callable

from src.application.dto import (
    ExtractSchemaDTO,
    GetConnectionDTO,
    ListConnectionsDTO,
    QueryResultDTO,
    RegisterConnectionDTO,
    RunText2SQLDTO,
    SchemaResultDTO,
)
from src.application.use_cases.extract_schema import ExtractSchema
from src.application.use_cases.get_connection import GetConnection
from src.application.use_cases.list_connections import ListConnections
from src.application.use_cases.register_connection import RegisterConnectionUseCase
from src.application.use_cases.run_text2sql import RunText2SQL
from src.domain.models import DatabaseConnection
from src.domain.ports.connection_verifier import IConnectionVerifier
from src.domain.ports.query_executor import IQueryExecutor
from src.domain.ports.schema_extractor import ISchemaExtractor
from src.domain.ports.unit_of_work import IUnitOfWork

logger = logging.getLogger(__name__)


class DBService:
    def __init__(
        self,
        uow_factory: Callable[[], IUnitOfWork],
        connection_verifier: IConnectionVerifier,
        query_executor: IQueryExecutor,
        schema_extractor: ISchemaExtractor,
    ) -> None:
        self._uow_factory = uow_factory
        self._connection_verifier = connection_verifier
        self._query_executor = query_executor
        self._schema_extractor = schema_extractor

    async def register_connection(self, dto: RegisterConnectionDTO) -> DatabaseConnection:
        return await RegisterConnectionUseCase(
            self._uow_factory(), self._connection_verifier
        ).execute(dto)

    async def list_connections(self, dto: ListConnectionsDTO) -> list[DatabaseConnection]:
        return await ListConnections(self._uow_factory()).execute(dto)

    async def get_connection(self, dto: GetConnectionDTO) -> DatabaseConnection:
        return await GetConnection(self._uow_factory()).execute(dto)

    async def run_text2sql(self, dto: RunText2SQLDTO) -> QueryResultDTO:
        return await RunText2SQL(self._uow_factory(), self._query_executor).execute(dto)

    async def extract_schema(self, dto: ExtractSchemaDTO) -> SchemaResultDTO:
        return await ExtractSchema(self._uow_factory(), self._schema_extractor).execute(dto)

    async def refresh_schema(self, dto: ExtractSchemaDTO) -> None:
        try:
            await self.extract_schema(dto)
        except Exception:
            logger.exception("Background schema extraction failed for %s", dto.connection_id)
