"""Voice agent API routes."""

from fastapi import APIRouter, Depends

from config.settings import Settings, get_settings
from services.voice_agent.request_dtos import TokenRequest
from services.voice_agent.response_dtos import HealthResponse, TokenResponse
from services.voice_agent.service import VoiceAgentService

router = APIRouter(prefix="/api/voice", tags=["voice"])


def _get_service(settings: Settings = Depends(get_settings)) -> VoiceAgentService:
    return VoiceAgentService(settings)


@router.post("/token", response_model=TokenResponse)
async def generate_token(
    request: TokenRequest,
    service: VoiceAgentService = Depends(_get_service),
) -> TokenResponse:
    return await service.generate_token(request)


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    return HealthResponse()
