from __future__ import annotations

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from typing import Any

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

logger = logging.getLogger(__name__)

_DLQ_SUFFIX = ".dlq"
_DLQ_SEND_TIMEOUT_S = 5


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
        self._producer: AIOKafkaProducer | None = None
        self._tasks: list[asyncio.Task] = []

    @property
    def _started_consumer(self) -> AIOKafkaConsumer:
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
        self._producer = AIOKafkaProducer(
            bootstrap_servers=self._bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            acks="all",
            enable_idempotence=True,
        )

        await self._consumer.start()
        await self._producer.start()

        logger.info(
            "Kafka consumer started | topics=%s group=%s",
            self._topics,
            self._group_id,
        )
        self._tasks.append(asyncio.create_task(self._consume(0)))

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
        if self._producer is not None:
            await self._producer.stop()
            self._producer = None
        logger.info("Kafka consumer stopped")

    async def _consume(self, worker_id: int) -> None:
        logger.info("Consumer worker %d started", worker_id)
        consumer = self._started_consumer
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
        try:
            envelope = msg.value
            event_type: str = envelope.get("type", "")
            raw_payload: str | dict = envelope.get("payload", {})

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
            await consumer.commit()

        except Exception:
            logger.exception(
                "Worker %d failed to process message | topic=%s partition=%d offset=%d",
                worker_id,
                msg.topic,
                msg.partition,
                msg.offset,
            )
            await self._send_to_dlq(msg)
            await consumer.commit()

    async def _send_to_dlq(self, msg: Any) -> None:
        if self._producer is None:
            logger.error(
                "DLQ_SEND_FAILED | producer not initialised — message lost | "
                "topic=%s partition=%d offset=%d",
                msg.topic,
                msg.partition,
                msg.offset,
            )
            return

        dlq_topic = f"{msg.topic}{_DLQ_SUFFIX}"
        dlq_record = {
            "dlq_metadata": {
                "original_topic": msg.topic,
                "original_partition": msg.partition,
                "original_offset": msg.offset,
                "consumer_group": self._group_id,
            },
            "original_value": msg.value,
        }

        try:
            await asyncio.wait_for(
                self._producer.send_and_wait(
                    dlq_topic,
                    value=dlq_record,
                    key=msg.key,
                ),
                timeout=_DLQ_SEND_TIMEOUT_S,
            )
            logger.warning(
                "DLQ_SEND_OK | topic=%s partition=%d offset=%d → %s",
                msg.topic,
                msg.partition,
                msg.offset,
                dlq_topic,
            )
        except Exception:
            logger.error(
                "DLQ_SEND_FAILED | could not write to %s — message lost | "
                "topic=%s partition=%d offset=%d",
                dlq_topic,
                msg.topic,
                msg.partition,
                msg.offset,
                exc_info=True,
            )
