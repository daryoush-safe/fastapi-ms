from __future__ import annotations

import json
from collections.abc import AsyncIterator

import httpx

from src.domain.ports.sql_generator import ISqlGenerator


class SseSqlGenerator(ISqlGenerator):
    def __init__(
        self,
        base_url: str,
        stream_path: str = "/stream-query",
        timeout: float = 120.0,
    ) -> None:
        self._url = base_url.rstrip("/") + stream_path
        self._timeout = timeout

    async def stream(self, question: str, schema: str) -> AsyncIterator[dict]:
        payload = {"question": question, "schema": schema}
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            async with client.stream("POST", self._url, json=payload) as response:
                if response.status_code >= 400:
                    body = (await response.aread()).decode("utf-8", "replace")
                    raise RuntimeError(f"ML service returned {response.status_code}: {body}")
                async for line in response.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    data = line[6:].strip()
                    if data == "[DONE]":
                        break
                    try:
                        yield json.loads(data)
                    except json.JSONDecodeError:
                        continue
