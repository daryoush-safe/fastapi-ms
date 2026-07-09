import uuid

from sqlalchemy import inspect
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from src.domain.models import ColumnInfo, DatabaseSchema, TableSchema
from src.domain.ports.schema_extractor import ISchemaExtractor
from src.infrastructure.dsn import to_async_url


class SqlAlchemySchemaExtractor(ISchemaExtractor):
    async def execute(self, engine: str, dsn: str, connection_id: uuid.UUID) -> DatabaseSchema:
        eng = create_async_engine(to_async_url(engine, dsn))
        try:
            async with eng.connect() as conn:
                tables = await conn.run_sync(self._reflect)
        finally:
            await eng.dispose()
        return DatabaseSchema(connection_id=connection_id, tables=tables)

    @staticmethod
    def _reflect(sync_conn: Connection) -> list[TableSchema]:
        inspector = inspect(sync_conn)
        tables: list[TableSchema] = []
        for table_name in inspector.get_table_names():
            pk_cols = set(inspector.get_pk_constraint(table_name).get("constrained_columns") or [])
            columns = [
                ColumnInfo(
                    name=col["name"],
                    type=str(col["type"]),
                    nullable=bool(col.get("nullable", True)),
                    primary_key=col["name"] in pk_cols,
                )
                for col in inspector.get_columns(table_name)
            ]
            tables.append(TableSchema(name=table_name, columns=columns))
        return tables
