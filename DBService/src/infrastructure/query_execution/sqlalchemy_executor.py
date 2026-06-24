import uuid
from datetime import datetime, timezone

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from src.domain.models import QueryResult
from src.domain.ports.query_executor import IQueryExecutor


class SqlAlchemyQueryExecutor(IQueryExecutor):
    async def execute(
        self, dsn: str, sql: str, connection_id: uuid.UUID, prompt: str
    ) -> QueryResult:
        engine = create_async_engine(dsn)
        try:
            async with engine.connect() as conn:
                result = await conn.execute(text(sql))
                columns = list(result.keys())
                rows = [list(row) for row in result.fetchall()]
        finally:
            await engine.dispose()
        return QueryResult(
            connection_id=connection_id,
            prompt=prompt,
            generated_sql=sql,
            columns=columns,
            rows=rows,
            executed_at=datetime.now(timezone.utc),
        )
