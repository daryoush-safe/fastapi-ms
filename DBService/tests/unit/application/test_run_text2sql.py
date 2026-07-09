import uuid
from unittest.mock import AsyncMock

import pytest
from src.application.dto import RunText2SQLDTO
from src.application.use_cases.run_text2sql import RunText2SQL
from src.domain.exceptions import (
    ConnectionAccessDenied,
    ConnectionNotFound,
    SQLValidationError,
)
from src.domain.models import DatabaseConnection


@pytest.fixture
def mock_uow():
    uow = AsyncMock()
    uow.__aenter__.return_value = uow
    uow.__aexit__.return_value = None
    return uow


def _make_use_case(mock_uow):
    return RunText2SQL(uow=mock_uow, query_executor=AsyncMock())


async def test_connection_not_found(mock_uow):
    mock_uow.connections.get.return_value = None
    use_case = _make_use_case(mock_uow)
    with pytest.raises(ConnectionNotFound):
        await use_case.execute(
            RunText2SQLDTO(
                connection_id=uuid.uuid4(),
                owner_id=uuid.uuid4(),
                sql="SELECT 1",
            )
        )


async def test_connection_owned_by_another_user_is_denied(mock_uow):
    conn_id = uuid.uuid4()
    mock_uow.connections.get.return_value = DatabaseConnection(
        id=conn_id,
        owner_id=uuid.uuid4(),  # owned by someone else
        name="test-db",
        engine="sqlite",
        dsn="sqlite+aiosqlite:///:memory:",
        schema_cache=None,
        is_active=True,
    )
    use_case = _make_use_case(mock_uow)
    with pytest.raises(ConnectionAccessDenied):
        await use_case.execute(
            RunText2SQLDTO(
                connection_id=conn_id,
                owner_id=uuid.uuid4(),  # a different caller
                sql="SELECT 1",
            )
        )


async def test_non_readonly_sql_is_rejected(mock_uow):
    conn_id = uuid.uuid4()
    owner_id = uuid.uuid4()
    mock_uow.connections.get.return_value = DatabaseConnection(
        id=conn_id,
        owner_id=owner_id,
        name="test-db",
        engine="sqlite",
        dsn="sqlite+aiosqlite:///:memory:",
        schema_cache=None,
        is_active=True,
    )
    query_executor = AsyncMock()
    use_case = RunText2SQL(uow=mock_uow, query_executor=query_executor)
    with pytest.raises(SQLValidationError):
        await use_case.execute(
            RunText2SQLDTO(
                connection_id=conn_id,
                owner_id=owner_id,
                sql="DELETE FROM users",
            )
        )
    query_executor.execute.assert_not_awaited()
