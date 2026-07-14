from __future__ import annotations

import json
import uuid
from collections.abc import AsyncIterator
from datetime import datetime, timezone

from src.application.dto import SendMessageDTO
from src.domain.exceptions import SchemaUnavailable, ThreadAccessDenied, ThreadNotFound
from src.domain.models import ChatMessage, MessageRole
from src.domain.ports.sql_generator import ISqlGenerator
from src.domain.ports.unit_of_work import IUnitOfWork

_TITLE_MAX_WORDS = 8
_TITLE_MAX_CHARS = 80
_MAX_STORED_ROWS = 1000


class SendMessage:
    def __init__(self, uow: IUnitOfWork, sql_generator: ISqlGenerator) -> None:
        self._uow = uow
        self._sql_generator = sql_generator

    async def execute(self, dto: SendMessageDTO, access_token: str) -> AsyncIterator[str]:
        async with self._uow as uow:
            thread = await uow.threads.get(dto.thread_id)
            if thread is None:
                raise ThreadNotFound(dto.thread_id)
            if thread.user_id != dto.user_id:
                raise ThreadAccessDenied(dto.thread_id)

            ref = await uow.connections.get(thread.connection_id)
            if ref is None or not ref.schema:
                raise SchemaUnavailable(thread.connection_id)
            schema = ref.schema
            connection_id = thread.connection_id

            now = datetime.now(timezone.utc)
            await uow.messages.add(
                ChatMessage(
                    id=uuid.uuid4(),
                    thread_id=thread.id,
                    role=MessageRole.USER,
                    content=dto.question,
                    sql=None,
                    created_at=now,
                )
            )
            if not thread.title:
                thread.title = self._derive_title(dto.question)
            thread.last_message_at = now
            thread.updated_at = now
            await uow.threads.update(thread)

        return self._stream(dto, schema, connection_id, access_token)

    async def _stream(
        self,
        dto: SendMessageDTO,
        schema: str,
        connection_id: uuid.UUID,
        access_token: str,
    ) -> AsyncIterator[str]:
        final_sql: str | None = None
        final_answer: str | None = None
        final_chart: dict | None = None
        final_columns: list | None = None
        final_rows: list | None = None
        try:
            async for chunk in self._sql_generator.stream(
                dto.question,
                schema,
                db_id=connection_id,
                thread_id=dto.thread_id,
                access_token=access_token,
            ):
                for _node, updates in chunk.items():
                    if not isinstance(updates, dict):
                        continue
                    if updates.get("sql"):
                        final_sql = updates["sql"]
                    if updates.get("answer"):
                        final_answer = updates["answer"]
                    if updates.get("chart") is not None:
                        final_chart = updates["chart"]
                    if updates.get("columns") is not None:
                        final_columns = updates["columns"]
                    if updates.get("rows") is not None:
                        final_rows = updates["rows"]
                yield f"data: {json.dumps(chunk)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        finally:
            yield "data: [DONE]\n\n"
            await self._persist_answer(
                dto.thread_id, final_sql, final_answer, final_chart, final_columns, final_rows
            )

    async def _persist_answer(
        self,
        thread_id: uuid.UUID,
        final_sql: str | None,
        final_answer: str | None,
        final_chart: dict | None = None,
        final_columns: list | None = None,
        final_rows: list | None = None,
    ) -> None:
        if final_sql is None and final_answer is None:
            return
        if final_rows is not None:
            stored_rows = final_rows[:_MAX_STORED_ROWS]
            stored_columns = final_columns
        else:
            stored_rows = None
            stored_columns = None
            final_chart = None
        now = datetime.now(timezone.utc)
        async with self._uow as uow:
            await uow.messages.add(
                ChatMessage(
                    id=uuid.uuid4(),
                    thread_id=thread_id,
                    role=MessageRole.ASSISTANT,
                    content=final_answer,
                    sql=final_sql,
                    chart=final_chart,
                    columns=stored_columns,
                    rows=stored_rows,
                    created_at=now,
                )
            )
            thread = await uow.threads.get(thread_id)
            if thread is not None:
                thread.last_message_at = now
                thread.updated_at = now
                await uow.threads.update(thread)

    @staticmethod
    def _derive_title(question: str) -> str:
        words = question.strip().split()
        title = " ".join(words[:_TITLE_MAX_WORDS])
        if len(title) > _TITLE_MAX_CHARS:
            title = title[:_TITLE_MAX_CHARS].rstrip()
        return title or "New chat"
