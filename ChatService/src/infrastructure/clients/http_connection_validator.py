from __future__ import annotations

import uuid

import httpx

from src.domain.exceptions import (
    ConnectionAccessDenied,
    ConnectionNotFound,
    ConnectionServiceError,
)
from src.domain.ports.connection_validator import IConnectionValidator


class HttpConnectionValidator(IConnectionValidator):
    def __init__(self, base_url: str, timeout: float = 10.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    async def validate(self, connection_id: uuid.UUID, access_token: str) -> None:
        url = f"{self._base_url}/api/v1/connections/{connection_id}"
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(url, headers=headers)
        except httpx.HTTPError as e:
            raise ConnectionServiceError(str(e)) from e

        if response.status_code == 200:
            return
        if response.status_code == 404:
            raise ConnectionNotFound(connection_id)
        if response.status_code == 403:
            raise ConnectionAccessDenied(connection_id)
        if response.status_code == 401:
            raise ConnectionServiceError("DBService rejected the access token")
        raise ConnectionServiceError(f"DBService returned {response.status_code}")
