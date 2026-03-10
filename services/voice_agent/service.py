"""Voice agent service - token generation."""

import asyncio

from livekit.api import AccessToken, CreateAgentDispatchRequest, LiveKitAPI, VideoGrants

from config.settings import Settings
from pkg.logger import get_logger
from services.voice_agent.constants import AGENT_NAME
from services.voice_agent.errors import TokenGenerationError
from services.voice_agent.request_dtos import TokenRequest
from services.voice_agent.response_dtos import TokenResponse

logger = get_logger(__name__)


class VoiceAgentService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def generate_token(self, request: TokenRequest) -> TokenResponse:
        try:
            token = (
                AccessToken(
                    api_key=self._settings.livekit_api_key,
                    api_secret=self._settings.livekit_api_secret,
                )
                .with_identity(request.participant_name)
                .with_name(request.participant_name)
                .with_grants(
                    VideoGrants(
                        room_join=True,
                        room=request.room_name,
                    )
                )
                .to_jwt()
            )

            # Dispatch the agent to this room
            await self._dispatch_agent(request.room_name)

            logger.info(
                "token_generated",
                room=request.room_name,
                participant=request.participant_name,
            )

            return TokenResponse(
                token=token,
                livekit_url=self._settings.livekit_endpoint,
                room_name=request.room_name,
            )
        except Exception as e:
            logger.error("token_generation_failed", error=str(e))
            raise TokenGenerationError(f"Failed to generate token: {e}") from e

    async def _dispatch_agent(self, room_name: str) -> None:
        """Create an agent dispatch so the agent worker joins the room."""
        api = LiveKitAPI(
            url=self._settings.livekit_endpoint,
            api_key=self._settings.livekit_api_key,
            api_secret=self._settings.livekit_api_secret,
        )
        try:
            await api.agent_dispatch.create_dispatch(
                CreateAgentDispatchRequest(
                    room=room_name,
                    agent_name=AGENT_NAME,
                )
            )
            logger.info("agent_dispatched", room=room_name, agent_name=AGENT_NAME)
        except Exception as e:
            logger.warning("agent_dispatch_failed", error=str(e), room=room_name)
        finally:
            await api.aclose()
