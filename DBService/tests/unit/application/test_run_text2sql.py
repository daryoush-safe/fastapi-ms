import uuid
from unittest.mock import AsyncMock

import pytest

from DBService.src.application.dto import RunText2SQLCommand
from DBService.src.application.use_cases.run_text2sql import RunText2SQL
from DBService.src.domain.exceptions import ConnectionNotFound


@pytest.fixture
def mock_uow():
    uow = AsyncMock()
    uow.__aenter__.return_value = uow
    uow.__aexit__.return_value = None
    return uow


async def test_connection_not_found(mock_uow):
    mock_uow.connections.get.return_value = None
    use_case = RunText2SQL(
        uow=mock_uow,
        schema_reader=AsyncMock(),
        sql_generator=AsyncMock(),
        query_executor=AsyncMock(),
        publisher=AsyncMock(),
    )
    with pytest.raises(ConnectionNotFound):
        await use_case.execute(
            RunText2SQLCommand(connection_id=uuid.uuid4(), prompt="How many users?")
        )
