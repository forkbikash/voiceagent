"""Response DTOs for voice agent service."""

from pydantic import BaseModel


class TokenResponse(BaseModel):
    token: str
    livekit_url: str
    room_name: str


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "voice-agent"
