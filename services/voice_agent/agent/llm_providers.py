"""Concrete LLM provider implementations."""

from collections.abc import AsyncGenerator
from typing import Any

from livekit.agents.llm import ChatChunk
from livekit.plugins import google

from services.voice_agent.ios import LLMProviderInterface


class GeminiLLMProvider(LLMProviderInterface):
    """Wraps a Google Gemini model as an LLM provider."""

    def __init__(self, model: str, api_key: str | None = None) -> None:
        self._model_name = model
        kwargs: dict[str, Any] = {"model": model}
        if api_key:
            kwargs["api_key"] = api_key
        self._llm = google.LLM(**kwargs)

    @property
    def name(self) -> str:
        return f"gemini:{self._model_name}"

    async def stream_chat(
        self, chat_ctx: Any, tools: Any | None = None
    ) -> AsyncGenerator[ChatChunk, None]:
        kwargs: dict[str, Any] = {"chat_ctx": chat_ctx}
        if tools:
            kwargs["tools"] = tools
        async with self._llm.chat(**kwargs) as stream:
            async for chunk in stream:
                yield chunk
