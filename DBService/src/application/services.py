from collections.abc import Callable

from src.application.dto import (
    ExtractSchemaDTO,
    QueryResultDTO,
    RegisterConnectionDTO,
    RunText2SQLDTO,
    SchemaResultDTO,
)
from src.application.use_cases.extract_schema import ExtractSchema
from src.application.use_cases.register_connection import RegisterConnectionUseCase
from src.application.use_cases.run_text2sql import RunText2SQL
from src.domain.models import DatabaseConnection
from src.domain.ports.connection_verifier import IConnectionVerifier
from src.domain.ports.query_executor import IQueryExecutor
from src.domain.ports.schema_extractor import ISchemaExtractor
from src.domain.ports.unit_of_work import IUnitOfWork


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

    async def run_text2sql(self, dto: RunText2SQLDTO) -> QueryResultDTO:
        return await RunText2SQL(self._uow_factory(), self._query_executor).execute(dto)

    async def extract_schema(self, dto: ExtractSchemaDTO) -> SchemaResultDTO:
        return await ExtractSchema(self._uow_factory(), self._schema_extractor).execute(dto)
