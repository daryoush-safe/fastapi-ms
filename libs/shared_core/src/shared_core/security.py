from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt


class TokenError(Exception):
    """Raised when a token is missing, malformed, expired or has a bad signature."""


def create_access_token(
    *,
    subject: str,
    email: str,
    secret: str,
    algorithm: str = "HS256",
    expires_minutes: int = 30,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "email": email,
        "iat": now,
        "exp": now + timedelta(minutes=expires_minutes),
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, secret, algorithm=algorithm)


def decode_access_token(
    token: str,
    *,
    secret: str,
    algorithms: list[str],
) -> dict[str, Any]:
    try:
        return jwt.decode(token, secret, algorithms=algorithms)
    except jwt.PyJWTError as exc:
        raise TokenError(str(exc)) from exc
