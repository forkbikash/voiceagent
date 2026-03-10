"""Racing LLM coordinator - races multiple providers and uses the fastest."""

import asyncio
from collections.abc import AsyncGenerator
from typing import Any

from livekit.agents.llm import ChatChunk

from pkg.logger import get_logger
from services.voice_agent.ios import LLMProviderInterface

logger = get_logger(__name__)

_RACE_TIMEOUT_SECONDS = 30


class RacingLLM:
    """Races multiple LLM providers in parallel, first-chunk-wins."""

    def __init__(self, providers: list[LLMProviderInterface]) -> None:
        if not providers:
            raise ValueError("At least one LLM provider is required")
        self._providers = providers

    async def race_chat(
        self, chat_ctx: Any, tools: Any | None = None
    ) -> AsyncGenerator[ChatChunk, None]:
        """Race all providers. First to yield a chunk wins; losers are cancelled."""
        queue: asyncio.Queue[tuple[int, ChatChunk | None, BaseException | None]] = (
            asyncio.Queue()
        )

        async def _run_provider(idx: int, provider: LLMProviderInterface) -> None:
            try:
                stream = provider.stream_chat(chat_ctx, tools)
                async for chunk in stream:
                    await queue.put((idx, chunk, None))
            except asyncio.CancelledError:
                # Loser was cancelled — don't report as error, don't send sentinel
                return
            except Exception as e:
                await queue.put((idx, None, e))
                # Don't fall through to finally sentinel — error message is enough
                return
            # Normal completion sentinel (only reached if no error/cancel)
            await queue.put((idx, None, None))

        tasks = [
            asyncio.create_task(_run_provider(i, p))
            for i, p in enumerate(self._providers)
        ]

        winner_idx: int | None = None
        finished: set[int] = set()

        try:
            while True:
                try:
                    idx, chunk, error = await asyncio.wait_for(
                        queue.get(), timeout=_RACE_TIMEOUT_SECONDS
                    )
                except asyncio.TimeoutError:
                    logger.error(
                        "llm_race_timeout",
                        timeout_seconds=_RACE_TIMEOUT_SECONDS,
                        winner=self._providers[winner_idx].name if winner_idx is not None else None,
                    )
                    return

                if error is not None:
                    logger.warning(
                        "llm_provider_error",
                        provider=self._providers[idx].name,
                        error=str(error),
                    )
                    finished.add(idx)
                    # If the winner errored, no point waiting (losers are cancelled)
                    if idx == winner_idx:
                        logger.error("llm_winner_failed_mid_stream", provider=self._providers[idx].name)
                        return
                    if len(finished) == len(self._providers):
                        logger.error("all_llm_providers_failed")
                        return
                    continue

                if chunk is None:
                    finished.add(idx)
                    if idx == winner_idx or len(finished) == len(self._providers):
                        return
                    continue

                if winner_idx is None:
                    winner_idx = idx
                    logger.info(
                        "llm_race_winner",
                        winner=self._providers[idx].name,
                        total_providers=len(self._providers),
                    )
                    # Cancel losers
                    for i, task in enumerate(tasks):
                        if i != winner_idx:
                            task.cancel()

                if idx == winner_idx:
                    yield chunk
        finally:
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
