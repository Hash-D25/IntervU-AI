"""Feedback generator contract."""

from typing import Protocol

from app.features.feedback.schemas import FeedbackContext, FeedbackResult


class FeedbackGenerator(Protocol):
    @property
    def name(self) -> str: ...

    async def generate(self, context: FeedbackContext) -> FeedbackResult: ...
