"""Google ID token verification for SSO."""

from typing import Any

import jwt
import structlog
from jwt import PyJWKClient

from app.core.exceptions import UnauthorizedError

log = structlog.get_logger(__name__)

_GOOGLE_ISSUERS = frozenset({"accounts.google.com", "https://accounts.google.com"})
_JWKS_CLIENT = PyJWKClient("https://www.googleapis.com/oauth2/v3/certs", cache_keys=True)


def verify_google_id_token(token: str, client_id: str) -> dict[str, Any]:
    """Validate a Google Identity Services credential and return its claims."""
    normalized_client_id = client_id.strip().strip('"').strip("'")
    if not normalized_client_id:
        raise UnauthorizedError("Invalid Google sign-in token")

    try:
        signing_key = _JWKS_CLIENT.get_signing_key_from_jwt(token)
        claims: dict[str, Any] = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=normalized_client_id,
            leeway=30,
        )
    except jwt.InvalidAudienceError as exc:
        log.warning(
            "google_id_token_audience_mismatch",
            expected=normalized_client_id,
            error=str(exc),
        )
        raise UnauthorizedError(
            "Invalid Google sign-in token. Ensure GOOGLE_CLIENT_ID matches "
            "NEXT_PUBLIC_GOOGLE_CLIENT_ID on the frontend."
        ) from exc
    except jwt.PyJWTError as exc:
        log.warning("google_id_token_verification_failed", error=type(exc).__name__, detail=str(exc))
        raise UnauthorizedError("Invalid Google sign-in token") from exc

    if claims.get("iss") not in _GOOGLE_ISSUERS:
        raise UnauthorizedError("Invalid Google sign-in token")

    token_aud = claims.get("aud")
    token_azp = claims.get("azp")
    if token_aud != normalized_client_id and token_azp != normalized_client_id:
        log.warning(
            "google_id_token_audience_mismatch",
            expected=normalized_client_id,
            aud=token_aud,
            azp=token_azp,
        )
        raise UnauthorizedError(
            "Invalid Google sign-in token. Ensure GOOGLE_CLIENT_ID matches "
            "NEXT_PUBLIC_GOOGLE_CLIENT_ID on the frontend."
        )

    return claims
