from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from src.domain.ports.connection_verifier import IConnectionVerifier
from src.infrastructure.dsn import to_async_url


class SqlAlchemyConnectionVerifier(IConnectionVerifier):
    async def verify(self, engine: str, dsn: str) -> None:
        eng = create_async_engine(to_async_url(engine, dsn))
        try:
            async with eng.connect() as conn:
                await conn.execute(text("SELECT 1"))
        finally:
            await eng.dispose()
