"""Authentication business logic.

``AuthService`` owns the transaction boundary: repositories flush, the service
commits. It coordinates the user and refresh-token repositories with the crypto
primitives in ``app.core.security``.
"""

from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security.passwords import hash_password, verify_password
from app.core.security.tokens import (
    create_access_token,
    generate_refresh_token,
    hash_refresh_token,
)
from app.features.auth.models import RefreshToken
from app.features.auth.repository import RefreshTokenRepository
from app.features.auth.schemas import RegisterRequest, TokenResponse
from app.features.user.models import User
from app.features.user.repository import UserRepository


class AuthService:
    def __init__(
        self,
        session: AsyncSession,
        users: UserRepository,
        refresh_tokens: RefreshTokenRepository,
        settings: Settings,
    ) -> None:
        self._session = session
        self._users = users
        self._refresh_tokens = refresh_tokens
        self._settings = settings

    async def register(self, data: RegisterRequest) -> User:
        if await self._users.get_by_email(data.email) is not None:
            raise ConflictError("Email is already registered")

        user = await self._users.add(
            User(
                email=data.email,
                full_name=data.full_name,
                hashed_password=hash_password(data.password),
            )
        )
        await self._session.commit()
        return user

    async def login(self, email: str, password: str) -> TokenResponse:
        user = await self._users.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise UnauthorizedError("Invalid email or password")

        tokens = await self._issue_tokens(user)
        await self._session.commit()
        return tokens

    async def refresh(self, raw_refresh_token: str) -> TokenResponse:
        record = await self._refresh_tokens.get_active_by_hash(
            hash_refresh_token(raw_refresh_token)
        )
        if record is None:
            raise UnauthorizedError("Invalid or expired refresh token")

        await self._refresh_tokens.revoke(record)
        user = await self._users.get(record.user_id)
        if user is None:
            raise UnauthorizedError("Invalid or expired refresh token")

        tokens = await self._issue_tokens(user)
        await self._session.commit()
        return tokens

    async def logout(self, raw_refresh_token: str) -> None:
        record = await self._refresh_tokens.get_by_hash(hash_refresh_token(raw_refresh_token))
        if record is not None and record.revoked_at is None:
            await self._refresh_tokens.revoke(record)
        await self._session.commit()

    async def _issue_tokens(self, user: User) -> TokenResponse:
        access_token = create_access_token(user.id, self._settings)
        raw_refresh_token, token_hash = generate_refresh_token()
        expires_at = datetime.now(UTC) + timedelta(days=self._settings.refresh_token_expire_days)
        await self._refresh_tokens.add(
            RefreshToken(user_id=user.id, token_hash=token_hash, expires_at=expires_at)
        )
        return TokenResponse(access_token=access_token, refresh_token=raw_refresh_token)
