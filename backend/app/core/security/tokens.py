"""JWT access tokens and opaque refresh tokens.

Access tokens are stateless JWTs. Refresh tokens are random opaque strings; only
their SHA-256 hash is ever persisted, so a database leak does not expose usable
tokens.
"""

import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

import jwt

from app.core.config import Settings
from app.core.exceptions import UnauthorizedError

_ACCESS_TOKEN_TYPE = "access"
_REFRESH_TOKEN_BYTES = 48


def create_access_token(user_id: UUID, settings: Settings) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": str(user_id),
        "type": _ACCESS_TOKEN_TYPE,
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_expire_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str, settings: Settings) -> dict[str, Any]:
    try:
        claims: dict[str, Any] = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
    except jwt.PyJWTError as exc:
        raise UnauthorizedError("Invalid or expired token") from exc

    if claims.get("type") != _ACCESS_TOKEN_TYPE:
        raise UnauthorizedError("Invalid token type")
    return claims


def hash_refresh_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode()).hexdigest()


def generate_refresh_token() -> tuple[str, str]:
    """Return ``(raw_token, token_hash)``. Only the hash should be stored."""
    raw_token = secrets.token_urlsafe(_REFRESH_TOKEN_BYTES)
    return raw_token, hash_refresh_token(raw_token)
