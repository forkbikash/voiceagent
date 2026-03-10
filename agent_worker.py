"""LiveKit agent worker entry point."""

from livekit import agents

from config.settings import get_settings
from pkg.logger import setup_logging
from services.voice_agent.agent.pipeline_factory import create_agent, create_session
from services.voice_agent.constants import AGENT_NAME

settings = get_settings()
settings.export_plugin_env_vars()
setup_logging(settings.environment)

server = agents.AgentServer()


@server.rtc_session(agent_name=AGENT_NAME)
async def entrypoint(ctx: agents.JobContext) -> None:
    agent = create_agent(settings)
    session = create_session()
    await session.start(room=ctx.room, agent=agent)
    await session.generate_reply(instructions="Greet the user warmly.")


if __name__ == "__main__":
    agents.cli.run_app(server)
