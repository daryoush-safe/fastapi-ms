from __future__ import annotations

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from typing import Any

from aiokafka import AIOKafkaConsumer

logger = logging.getLogger(__name__)


class BaseKafkaConsumer(ABC):
    def __init__(
        self,
        topics: list[str],
        bootstrap_servers: str,
        group_id: str,
        num_workers: int = 3,
        auto_offset_reset: str = "earliest",
        max_poll_interval_ms: int = 300_000,
        session_timeout_ms: int = 30_000,
    ) -> None:
        self._topics = topics
        self._bootstrap_servers = bootstrap_servers
        self._group_id = group_id
        self._num_workers = num_workers
        self._auto_offset_reset = auto_offset_reset
        self._max_poll_interval_ms = max_poll_interval_ms
        self._session_timeout_ms = session_timeout_ms
        self._consumer: AIOKafkaConsumer | None = None
        self._tasks: list[asyncio.Task] = []

    @property
    def _started_consumer(self) -> AIOKafkaConsumer:
        """Returns the consumer, raising clearly if start() was never called."""
        if self._consumer is None:
            raise RuntimeError("Consumer not started — call await start() first")
        return self._consumer

    @abstractmethod
    async def handle(self, event_type: str, payload: dict[str, Any]) -> None: ...

    async def start(self) -> None:
        self._consumer = AIOKafkaConsumer(
            *self._topics,
            bootstrap_servers=self._bootstrap_servers,
            group_id=self._group_id,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            enable_auto_commit=False,
            max_poll_interval_ms=self._max_poll_interval_ms,
            session_timeout_ms=self._session_timeout_ms,
            auto_offset_reset=self._auto_offset_reset,
        )
        await self._consumer.start()
        logger.info(
            "Kafka consumer started | topics=%s group=%s",
            self._topics,
            self._group_id,
        )
        for i in range(self._num_workers):
            self._tasks.append(asyncio.create_task(self._consume(i)))

    async def stop(self) -> None:
        logger.info("Stopping Kafka consumer…")
        for t in self._tasks:
            t.cancel()
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
            self._tasks.clear()
        if self._consumer is not None:
            await self._consumer.stop()
            self._consumer = None
        logger.info("Kafka consumer stopped")

    async def _consume(self, worker_id: int) -> None:
        logger.info("Consumer worker %d started", worker_id)
        consumer = self._started_consumer  # resolved once, never None
        try:
            async for msg in consumer:
                await self._process_message(consumer, worker_id, msg)
        except asyncio.CancelledError:
            logger.info("Consumer worker %d cancelled", worker_id)
            raise
        except Exception:
            logger.exception("Consumer worker %d crashed", worker_id)
        finally:
            logger.info("Consumer worker %d shutting down", worker_id)

    async def _process_message(
        self, consumer: AIOKafkaConsumer, worker_id: int, msg: Any
    ) -> None:
        """
        Debezium Outbox EventRouter envelope:
        {
          "payload": {
            "type": "<event_type>",
            "payload": "<json-string>"
          }
        }
        """
        try:
            envelope = msg.value
            inner = envelope.get("payload", {})
            event_type: str = inner.get("type", "")
            raw_payload: str | dict = inner.get("payload", "{}")

            payload: dict[str, Any] = (
                json.loads(raw_payload) if isinstance(raw_payload, str) else raw_payload
            )

            logger.info(
                "Worker %d | topic=%s event_type=%s",
                worker_id,
                msg.topic,
                event_type,
            )

            await self.handle(event_type, payload)
            await consumer.commit()  # consumer is AIOKafkaConsumer, never None

        except Exception:
            logger.exception(
                "Worker %d failed to process message — not committing", worker_id
            )
