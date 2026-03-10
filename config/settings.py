"""Application configuration via environment variables."""

import os
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    app_name: str = "interview-voice-agent"
    environment: str = "development"
    debug: bool = False

    # LiveKit
    livekit_endpoint: str = "ws://localhost:7880"
    livekit_api_key: str = ""
    livekit_api_secret: str = ""

    # ElevenLabs
    elevenlabs_key: str = ""

    # Gemini
    gemini_key: str = ""

    model_config = {"env_file": ".env", "extra": "ignore"}

    def export_plugin_env_vars(self) -> None:
        """Export env vars that LiveKit plugins and agent framework expect."""
        if self.elevenlabs_key:
            os.environ["ELEVEN_API_KEY"] = self.elevenlabs_key
        if self.gemini_key:
            os.environ["GOOGLE_API_KEY"] = self.gemini_key
        if self.livekit_endpoint:
            os.environ["LIVEKIT_URL"] = self.livekit_endpoint
        if self.livekit_api_key:
            os.environ["LIVEKIT_API_KEY"] = self.livekit_api_key
        if self.livekit_api_secret:
            os.environ["LIVEKIT_API_SECRET"] = self.livekit_api_secret


@lru_cache
def get_settings() -> Settings:
    return Settings()
