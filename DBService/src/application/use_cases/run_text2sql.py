from __future__ import annotations

import re

from src.application.dto import QueryResultDTO, RunText2SQLDTO
from src.domain.exceptions import (
    ConnectionAccessDenied,
    ConnectionNotFound,
    QueryExecutionError,
    SQLValidationError,
)
from src.domain.ports.query_executor import IQueryExecutor
from src.domain.ports.unit_of_work import IUnitOfWork

_FORBIDDEN = {
    "insert",
    "update",
    "delete",
    "drop",
    "truncate",
    "alter",
    "create",
    "grant",
    "revoke",
    "replace",
    "merge",
    "call",
    "attach",
    "commit",
    "rollback",
}

_COMMENT_RE = re.compile(r"--[^\n]*|/\*.*?\*/", re.DOTALL)


class RunText2SQL:
    def __init__(self, uow: IUnitOfWork, query_executor: IQueryExecutor) -> None:
        self._uow = uow
        self._query_executor = query_executor

    async def execute(self, dto: RunText2SQLDTO) -> QueryResultDTO:
        async with self._uow as uow:
            conn = await uow.connections.get(dto.connection_id)
            if conn is None:
                raise ConnectionNotFound(dto.connection_id)
            if conn.owner_id != dto.owner_id:
                raise ConnectionAccessDenied(dto.connection_id)
            engine, dsn = conn.engine, conn.dsn

        self._validate_readonly_sql(dto.sql)

        try:
            result = await self._query_executor.execute(engine, dsn, dto.sql, dto.connection_id)
        except Exception as e:
            raise QueryExecutionError(str(e)) from e

        return QueryResultDTO.from_domain(result)

    @staticmethod
    def _validate_readonly_sql(sql: str) -> None:
        stripped = _COMMENT_RE.sub(" ", sql).strip().rstrip(";").strip()
        if not stripped:
            raise SQLValidationError("empty statement")

        if ";" in stripped:
            raise SQLValidationError("multiple statements are not allowed")

        tokens = re.findall(r"[a-zA-Z_]+", stripped.lower())
        if not tokens:
            raise SQLValidationError("no SQL keywords found")

        if tokens[0] not in {"select", "with"}:
            raise SQLValidationError("only read-only SELECT queries are allowed")

        forbidden = _FORBIDDEN.intersection(tokens)
        if forbidden:
            raise SQLValidationError(f"disallowed keyword(s): {', '.join(sorted(forbidden))}")
