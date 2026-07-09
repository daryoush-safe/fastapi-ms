from __future__ import annotations

from urllib.parse import quote

SUPPORTED_ENGINES: frozenset[str] = frozenset({"postgres", "mysql", "sqlite"})

_URL_SCHEMES = {"postgres": "postgresql", "mysql": "mysql", "sqlite": "sqlite"}
_DEFAULT_PORTS = {"postgres": 5432, "mysql": 3306}


def is_supported_engine(engine: str) -> bool:
    return engine.lower() in SUPPORTED_ENGINES


def build_dsn(
    engine: str,
    *,
    host: str | None = None,
    port: int | None = None,
    username: str | None = None,
    password: str | None = None,
    database: str | None = None,
) -> str:
    engine = engine.lower()
    scheme = _URL_SCHEMES[engine]

    if engine == "sqlite":
        if not database:
            raise ValueError("sqlite connection requires a database file path")
        return f"sqlite:///{database}"

    if not host or not database:
        raise ValueError(f"{engine} connection requires both host and database")

    user_info = ""
    if username:
        user_info = quote(username, safe="")
        if password:
            user_info += f":{quote(password, safe='')}"
        user_info += "@"

    port = port or _DEFAULT_PORTS[engine]
    return f"{scheme}://{user_info}{host}:{port}/{database}"
