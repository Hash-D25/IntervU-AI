"""Auth dependency wiring.

``get_current_user`` is the single dependency business routes use to require
authentication — validation lives here as a composable dependency rather than
ASGI middleware, so it is per-route, typed, and visible in the OpenAPI schema.
"""

from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.container import SessionDep, SettingsDep
from app.core.exceptions import UnauthorizedError
from app.core.security.tokens import decode_access_token
from app.features.auth.repository import RefreshTokenRepository
from app.features.auth.service import AuthService
from app.features.user.models import User
from app.features.user.repository import UserRepository

_bearer_scheme = HTTPBearer(description="JWT access token")


def get_user_repository(session: SessionDep) -> UserRepository:
    return UserRepository(session)


def get_refresh_token_repository(session: SessionDep) -> RefreshTokenRepository:
    return RefreshTokenRepository(session)


def get_auth_service(
    session: SessionDep,
    settings: SettingsDep,
    users: Annotated[UserRepository, Depends(get_user_repository)],
    refresh_tokens: Annotated[RefreshTokenRepository, Depends(get_refresh_token_repository)],
) -> AuthService:
    return AuthService(session, users, refresh_tokens, settings)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer_scheme)],
    settings: SettingsDep,
    users: Annotated[UserRepository, Depends(get_user_repository)],
) -> User:
    claims = decode_access_token(credentials.credentials, settings)
    user = await users.get(UUID(claims["sub"]))
    if user is None:
        raise UnauthorizedError("User no longer exists")
    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]
