from __future__ import annotations

from sqlalchemy.engine import make_url

_ASYNC_DRIVERS = {
    "postgres": "postgresql+asyncpg",
    "mysql": "mysql+aiomysql",
    "sqlite": "sqlite+aiosqlite",
}


def to_async_url(engine: str, dsn: str) -> str:
    url = make_url(dsn)
    driver = _ASYNC_DRIVERS.get(engine.lower())
    if driver:
        url = url.set(drivername=driver)
    return url.render_as_string(hide_password=False)
