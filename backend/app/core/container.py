"""Dependency-injection wiring.

We use FastAPI's native ``Depends`` rather than a DI framework: it is explicit,
type-safe, and adds no magic. These ``Annotated`` aliases keep route and service
signatures short and consistent.
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.synthesis.base import SpeechSynthesizer
from app.ai.synthesis.factory import create_synthesizer
from app.core.config import Settings, get_settings
from app.db.session import get_session

SettingsDep = Annotated[Settings, Depends(get_settings)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_synthesizer(settings: SettingsDep) -> SpeechSynthesizer:
    return create_synthesizer(settings)


SpeechSynthesizerDep = Annotated[SpeechSynthesizer, Depends(get_synthesizer)]
