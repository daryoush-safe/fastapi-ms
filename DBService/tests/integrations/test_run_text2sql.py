import uuid
from unittest.mock import AsyncMock

import pytest
from src.application.dto import RunText2SQLDTO
from src.application.use_cases.run_text2sql import RunText2SQL
from src.domain.exceptions import QueryExecutionError
from src.domain.models import DatabaseConnection
from src.infrastructure.query_execution.sqlalchemy_executor import SqlAlchemyQueryExecutor


def _uow_returning(conn):
    mock_uow = AsyncMock()
    mock_uow.__aenter__.return_value = mock_uow
    mock_uow.__aexit__.return_value = None
    mock_uow.connections.get.return_value = conn
    return mock_uow


async def test_full_pipeline(target_sqlite_dsn):
    conn_id = uuid.uuid4()
    owner_id = uuid.uuid4()
    fake_conn = DatabaseConnection(
        id=conn_id,
        owner_id=owner_id,
        name="test-db",
        engine="sqlite",
        dsn=target_sqlite_dsn,
        schema_cache=None,
        is_active=True,
    )

    use_case = RunText2SQL(
        uow=_uow_returning(fake_conn),
        query_executor=SqlAlchemyQueryExecutor(),
    )
    result = await use_case.execute(
        RunText2SQLDTO(
            connection_id=conn_id,
            owner_id=owner_id,
            sql="SELECT id, name FROM items",
        )
    )

    assert result.columns == ["id", "name"]
    assert result.rows == [[1, "test"]]


async def test_execution_error_is_surfaced(target_sqlite_dsn):
    conn_id = uuid.uuid4()
    owner_id = uuid.uuid4()
    fake_conn = DatabaseConnection(
        id=conn_id,
        owner_id=owner_id,
        name="test-db",
        engine="sqlite",
        dsn=target_sqlite_dsn,
        schema_cache=None,
        is_active=True,
    )

    use_case = RunText2SQL(
        uow=_uow_returning(fake_conn),
        query_executor=SqlAlchemyQueryExecutor(),
    )
    with pytest.raises(QueryExecutionError):
        await use_case.execute(
            RunText2SQLDTO(
                connection_id=conn_id,
                owner_id=owner_id,
                sql="SELECT missing_column FROM items",
            )
        )
