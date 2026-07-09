"""Provider-agnostic LLM contract.

Business logic depends on this ``Protocol`` - never on a concrete SDK. Swapping
providers means adding an implementation that satisfies this interface; no
service code changes. Implementations arrive in the AI iteration.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal, Protocol, runtime_checkable

Role = Literal["system", "user", "assistant"]


@dataclass(frozen=True, slots=True)
class ChatMessage:
    role: Role
    content: str


@runtime_checkable
class LLMProvider(Protocol):
    """Minimal contract for text generation from a chat-style message list."""

    async def generate(self, messages: Sequence[ChatMessage]) -> str: ...
