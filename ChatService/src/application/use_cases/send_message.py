from __future__ import annotations

import json
import uuid
from collections.abc import AsyncIterator
from datetime import datetime, timezone

from src.application.dto import SendMessageDTO
from src.domain.exceptions import ThreadAccessDenied, ThreadNotFound
from src.domain.models import ChatMessage, MessageRole
from src.domain.ports.sql_generator import ISqlGenerator
from src.domain.ports.unit_of_work import IUnitOfWork

_TITLE_MAX_WORDS = 8
_TITLE_MAX_CHARS = 80


class SendMessage:
    def __init__(self, uow: IUnitOfWork, sql_generator: ISqlGenerator) -> None:
        self._uow = uow
        self._sql_generator = sql_generator

    async def execute(self, dto: SendMessageDTO) -> AsyncIterator[str]:
        async with self._uow as uow:
            thread = await uow.threads.get(dto.thread_id)
            if thread is None:
                raise ThreadNotFound(dto.thread_id)
            if thread.user_id != dto.user_id:
                raise ThreadAccessDenied(dto.thread_id)

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

        return self._stream(dto)

    async def _stream(self, dto: SendMessageDTO) -> AsyncIterator[str]:
        final_sql: str | None = None
        final_answer: str | None = None
        try:
            async for chunk in self._sql_generator.stream(dto.question, dto.schema):
                for _node, updates in chunk.items():
                    if not isinstance(updates, dict):
                        continue
                    if updates.get("sql"):
                        final_sql = updates["sql"]
                    if updates.get("final_answer"):
                        final_answer = updates["final_answer"]
                yield f"data: {json.dumps(chunk)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        finally:
            yield "data: [DONE]\n\n"
            await self._persist_answer(dto.thread_id, final_sql, final_answer)

    async def _persist_answer(
        self, thread_id: uuid.UUID, final_sql: str | None, final_answer: str | None
    ) -> None:
        if final_sql is None and final_answer is None:
            return
        now = datetime.now(timezone.utc)
        async with self._uow as uow:
            await uow.messages.add(
                ChatMessage(
                    id=uuid.uuid4(),
                    thread_id=thread_id,
                    role=MessageRole.ASSISTANT,
                    content=final_answer,
                    sql=final_sql,
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
