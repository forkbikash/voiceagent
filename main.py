"""FastAPI entry point for the voice agent API."""

from fastapi import FastAPI

from config.settings import get_settings
from pkg.error_handling.handlers import register_exception_handlers
from pkg.logger import setup_logging
from services.voice_agent.middlewares import add_cors_middleware
from services.voice_agent.routes import router as voice_router

settings = get_settings()
setup_logging(settings.environment)

app = FastAPI(title=settings.app_name, debug=settings.debug)

add_cors_middleware(app)
register_exception_handlers(app)
app.include_router(voice_router)
