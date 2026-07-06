"""Application-level exceptions and their HTTP translation.

Services raise ``AppError`` (or subclasses); the API layer never needs to know
how errors become responses.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    """Base class for expected, domain-level failures."""

    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message, status_code=404)


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Not authenticated") -> None:
        super().__init__(message, status_code=401)


class ConflictError(AppError):
    def __init__(self, message: str = "Resource already exists") -> None:
        super().__init__(message, status_code=409)


async def _handle_app_error(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


def register_exception_handlers(app: FastAPI) -> None:
    # FastAPI types handlers against the base ``Exception``; our handler is
    # narrower, which is safe here.
    app.add_exception_handler(AppError, _handle_app_error)  # type: ignore[arg-type]
