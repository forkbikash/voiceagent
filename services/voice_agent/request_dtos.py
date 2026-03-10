"""Request DTOs for voice agent service."""

from pydantic import BaseModel, Field


class TokenRequest(BaseModel):
    room_name: str = Field(..., min_length=1, max_length=128)
    participant_name: str = Field(..., min_length=1, max_length=128)
