import uuid
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from DBService.src.application.dto import RunText2SQLCommand
from DBService.src.application.use_cases.run_text2sql import RunText2SQL
from DBService.src.domain.models import DatabaseConnection
from DBService.src.infrastructure.db_introspection.sqlalchemy_schema_reader import (
    SqlAlchemySchemaReader,
)
from DBService.src.infrastructure.query_execution.sqlalchemy_executor import SqlAlchemyQueryExecutor
from DBService.src.infrastructure.sql_generation.pruner_generator import PrunerSQLGenerator


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

    mock_uow = AsyncMock()
    mock_uow.__aenter__.return_value = mock_uow
    mock_uow.__aexit__.return_value = None
    mock_uow.connections.get.return_value = fake_conn

    fake_request = httpx.Request("POST", "http://pruner/generate")
    fake_response = httpx.Response(200, json={"sql": "SELECT 1"})
    fake_response.request = fake_request
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=fake_response):
        async with httpx.AsyncClient() as client:
            use_case = RunText2SQL(
                uow=mock_uow,
                schema_reader=SqlAlchemySchemaReader(),
                sql_generator=PrunerSQLGenerator(base_url="http://pruner", client=client),
                query_executor=SqlAlchemyQueryExecutor(),
                publisher=AsyncMock(),
            )
            cmd = RunText2SQLCommand(
                connection_id=conn_id,
                owner_id=owner_id,
                prompt="What is the capital of France?",
            )
            result = await use_case.execute(cmd)

    assert result.generated_sql == "SELECT 1"
    assert result.rows == [[1]]
