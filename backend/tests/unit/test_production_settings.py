"""Production settings validation."""

import pytest

from app.core.config import Settings


def _settings(**overrides: object) -> Settings:
    base: dict[str, object] = {
        "database_url": "sqlite+aiosqlite://",
        "app_env": "production",
        "jwt_secret_key": "x" * 32,
    }
    base.update(overrides)
    return Settings(**base)  # type: ignore[arg-type]


def test_production_allows_strong_jwt_secret() -> None:
    _settings().validate_for_production()


def test_production_rejects_default_jwt_secret() -> None:
    settings = _settings(jwt_secret_key="dev-insecure-secret-change-me-in-every-real-environment")
    with pytest.raises(ValueError, match="JWT_SECRET_KEY"):
        settings.validate_for_production()


def test_production_rejects_short_jwt_secret() -> None:
    settings = _settings(jwt_secret_key="too-short")
    with pytest.raises(ValueError, match="32 characters"):
        settings.validate_for_production()


def test_development_skips_validation() -> None:
    settings = _settings(app_env="development", jwt_secret_key="dev-insecure-secret-change-me-in-every-real-environment")
    settings.validate_for_production()
