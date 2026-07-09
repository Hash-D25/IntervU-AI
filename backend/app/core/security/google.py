"""Google ID token verification for SSO."""

from typing import Any

import jwt
from jwt import PyJWKClient

from app.core.exceptions import UnauthorizedError

_GOOGLE_ISSUERS = frozenset({"accounts.google.com", "https://accounts.google.com"})
_JWKS_CLIENT = PyJWKClient("https://www.googleapis.com/oauth2/v3/certs", cache_keys=True)


def verify_google_id_token(token: str, client_id: str) -> dict[str, Any]:
    """Validate a Google Identity Services credential and return its claims."""
    try:
        signing_key = _JWKS_CLIENT.get_signing_key_from_jwt(token)
        claims: dict[str, Any] = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=client_id,
        )
    except jwt.PyJWTError as exc:
        raise UnauthorizedError("Invalid Google sign-in token") from exc

    if claims.get("iss") not in _GOOGLE_ISSUERS:
        raise UnauthorizedError("Invalid Google sign-in token")

    return claims
