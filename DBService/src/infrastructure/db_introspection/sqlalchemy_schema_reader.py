from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import create_async_engine

from src.domain.ports.schema_reader import ISchemaReader


class SqlAlchemySchemaReader(ISchemaReader):
    async def read_schema(self, dsn: str) -> dict:
        engine = create_async_engine(dsn)
        try:
            async with engine.connect() as conn:
                tables = await conn.run_sync(self._introspect)
        finally:
            await engine.dispose()
        return tables

    @staticmethod
    def _introspect(sync_conn) -> dict:
        inspector = inspect(sync_conn)
        return {
            table: [
                {"name": col["name"], "type": str(col["type"])}
                for col in inspector.get_columns(table)
            ]
            for table in inspector.get_table_names()
        }
