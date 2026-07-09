import uuid
from datetime import datetime, timezone

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from src.domain.models import QueryResult
from src.domain.ports.query_executor import IQueryExecutor
from src.infrastructure.dsn import to_async_url


class SqlAlchemyQueryExecutor(IQueryExecutor):
    async def execute(
        self, engine: str, dsn: str, sql: str, connection_id: uuid.UUID
    ) -> QueryResult:
        eng = create_async_engine(to_async_url(engine, dsn))
        try:
            async with eng.connect() as conn:
                result = await conn.execute(text(sql))
                columns = list(result.keys())
                rows = [list(row) for row in result.fetchall()]
        finally:
            await eng.dispose()
        return QueryResult(
            connection_id=connection_id,
            columns=columns,
            rows=rows,
            executed_at=datetime.now(timezone.utc),
        )
