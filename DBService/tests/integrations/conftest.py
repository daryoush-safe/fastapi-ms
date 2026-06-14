import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


@pytest.fixture
async def target_sqlite_dsn(tmp_path):
    dsn = f"sqlite+aiosqlite:///{tmp_path}/target.db"
    engine = create_async_engine(dsn)
    async with engine.begin() as conn:
        await conn.execute(text("CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT)"))
        await conn.execute(text("INSERT INTO items VALUES (1, 'test')"))
    await engine.dispose()
    return dsn
