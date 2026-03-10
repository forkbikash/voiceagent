"""Interfaces for voice agent service."""

from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from typing import Any


class LLMProviderInterface(ABC):
    """Abstract interface for LLM providers used in racing."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider display name for logging."""
        ...

    @abstractmethod
    def stream_chat(
        self, chat_ctx: Any, tools: Any | None = None
    ) -> AsyncGenerator[Any, None]:
        """Stream chat completion chunks."""
        ...
