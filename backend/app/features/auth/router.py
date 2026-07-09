"""Auth routes. Thin: validate input, delegate to the service, shape the response."""

from fastapi import APIRouter, status

from app.features.auth.dependencies import AuthServiceDep, CurrentUserDep
from app.features.auth.schemas import (
    GoogleLoginRequest,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.features.user.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, service: AuthServiceDep) -> User:
    return await service.register(data)


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, service: AuthServiceDep) -> TokenResponse:
    return await service.login(data.email, data.password)


@router.post("/google", response_model=TokenResponse)
async def google_login(data: GoogleLoginRequest, service: AuthServiceDep) -> TokenResponse:
    return await service.login_with_google(data.id_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(data: RefreshRequest, service: AuthServiceDep) -> TokenResponse:
    return await service.refresh(data.refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(data: RefreshRequest, service: AuthServiceDep) -> None:
    await service.logout(data.refresh_token)


@router.get("/me", response_model=UserResponse)
async def me(current_user: CurrentUserDep) -> User:
    return current_user
