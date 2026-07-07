"""Execution engine domain errors."""

from app.core.exceptions import BadRequestError


class InvalidTransitionError(BadRequestError):
    def __init__(self, message: str = "Invalid interview state transition") -> None:
        super().__init__(message)
