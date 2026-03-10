"""Factory for assembling the voice agent pipeline."""

from livekit.agents import AgentSession
from livekit.plugins import elevenlabs, google, silero

from config.settings import Settings
from services.voice_agent.agent.llm_providers import GeminiLLMProvider
from services.voice_agent.agent.racing_llm import RacingLLM
from services.voice_agent.ios import LLMProviderInterface
from services.voice_agent.agent.voice_agent import VoiceAgent
from services.voice_agent.constants import (
    AGENT_INSTRUCTIONS,
    GEMINI_FLASH_MODEL,
    GEMINI_PRO_MODEL,
)


def create_racing_llm(settings: Settings) -> RacingLLM:
    """Create the racing LLM with configured providers."""
    providers: list[LLMProviderInterface] = [
        GeminiLLMProvider(
            model=GEMINI_FLASH_MODEL,
            api_key=settings.gemini_key or None,
        ),
        GeminiLLMProvider(
            model=GEMINI_PRO_MODEL,
            api_key=settings.gemini_key or None,
        ),
    ]
    return RacingLLM(providers)


def create_agent(settings: Settings) -> VoiceAgent:
    """Create the voice agent with racing LLM."""
    racing_llm = create_racing_llm(settings)
    return VoiceAgent(
        instructions=AGENT_INSTRUCTIONS,
        racing_llm=racing_llm,
    )


def create_session() -> AgentSession:
    """Create an AgentSession with STT, TTS, VAD, and a placeholder LLM.

    The LLM here satisfies the session's requirement for generate_reply().
    Actual inference is handled by the VoiceAgent's llm_node override (racing).
    """
    return AgentSession(
        stt=elevenlabs.STT(language_code="en"),
        tts=elevenlabs.TTS(language="en"),
        vad=silero.VAD.load(),
        llm=google.LLM(model=GEMINI_FLASH_MODEL),
    )
