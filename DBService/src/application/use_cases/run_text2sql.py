from DBService.src.application.dto import QueryResultDTO, RunText2SQLCommand
from DBService.src.domain.events import QueryExecuted
from DBService.src.domain.exceptions import (
    ConnectionAccessDenied,
    ConnectionNotFound,
    QueryExecutionError,
    SchemaIntrospectionError,
    SQLGenerationError,
)
from DBService.src.domain.ports.publisher import IEventPublisher
from DBService.src.domain.ports.query_executor import IQueryExecutor
from DBService.src.domain.ports.schema_reader import ISchemaReader
from DBService.src.domain.ports.sql_generator import ISQLGenerator
from DBService.src.domain.ports.unit_of_work import IUnitOfWork


class RunText2SQL:
    def __init__(
        self,
        uow: IUnitOfWork,
        schema_reader: ISchemaReader,
        sql_generator: ISQLGenerator,
        query_executor: IQueryExecutor,
        publisher: IEventPublisher,
    ) -> None:
        self._uow = uow
        self._schema_reader = schema_reader
        self._sql_generator = sql_generator
        self._query_executor = query_executor
        self._publisher = publisher

    async def execute(self, cmd: RunText2SQLCommand) -> QueryResultDTO:
        async with self._uow as uow:
            conn = await uow.connections.get(cmd.connection_id)
            if conn is None:
                raise ConnectionNotFound(cmd.connection_id)
            if conn.owner_id != cmd.owner_id:
                raise ConnectionAccessDenied(cmd.connection_id)

            try:
                schema = await self._schema_reader.read_schema(conn.dsn)
            except Exception as e:
                raise SchemaIntrospectionError(str(e)) from e

            try:
                sql = await self._sql_generator.generate(schema, cmd.prompt)
            except Exception as e:
                raise SQLGenerationError(str(e)) from e

            try:
                result = await self._query_executor.execute(
                    conn.dsn, sql, cmd.connection_id, cmd.prompt
                )
            except Exception as e:
                raise QueryExecutionError(str(e)) from e

            await self._publisher.publish(
                QueryExecuted(
                    connection_id=cmd.connection_id,
                    prompt=cmd.prompt,
                    generated_sql=sql,
                )
            )
            return QueryResultDTO.from_domain(result)
