"""Custom voice agent with LLM racing."""

import datetime
from collections.abc import AsyncIterable
from typing import Any

from livekit.agents import Agent
from livekit.agents.llm import ChatChunk, ChatContext, function_tool

from pkg.logger import get_logger
from services.voice_agent.agent.racing_llm import RacingLLM

logger = get_logger(__name__)

_LOG = "/tmp/voice_agent_debug.log"


def _log(msg: str) -> None:
    """Write debug log to file (subprocess stdout is not captured in dev mode)."""
    try:
        with open(_LOG, "a") as f:
            f.write(f"{datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]} {msg}\n")
    except Exception:
        pass


class VoiceAgent(Agent):
    """Agent that overrides llm_node to race multiple LLM providers."""

    def __init__(
        self,
        *,
        instructions: str,
        racing_llm: RacingLLM,
    ) -> None:
        super().__init__(instructions=instructions)
        self._racing_llm = racing_llm
        _log(f"VoiceAgent initialized, num_tools={len(self._tools)}")

    async def llm_node(
        self,
        chat_ctx: ChatContext,
        tools: list[Any],
        model_settings: Any,
    ) -> AsyncIterable[ChatChunk | str]:
        _log(f"llm_node called, tools={len(tools)}")
        chunk_count = 0
        async for chunk in self._racing_llm.race_chat(chat_ctx, tools=tools):
            chunk_count += 1
            if chunk_count == 1:
                _log(f"llm_node first chunk received")
            yield chunk
        _log(f"llm_node done, total_chunks={chunk_count}")

    @function_tool(description="End the call when the user says goodbye or wants to hang up.")
    async def end_call(self) -> None:
        """End the current voice call."""
        _log("END_CALL tool invoked - shutting down session")
        logger.info("end_call_triggered")
        self.session.shutdown()
        _log("END_CALL shutdown scheduled")
