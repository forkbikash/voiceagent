# Voice Agent

A real-time voice assistant built on [LiveKit Agents](https://docs.livekit.io/agents/) that races multiple LLM providers in parallel for the fastest response. The first model to return a chunk wins and streams to the user — the rest are cancelled.

## Architecture

```
┌─────────────┐       ┌──────────────────┐       ┌─────────────────────┐
│   Client    │◄─────►│   LiveKit Server  │◄─────►│   Agent Worker      │
│ (Playground)│  WSS  │  (self-hosted)    │  WSS  │                     │
└─────────────┘       └──────────────────┘       │  ┌───────────────┐  │
                                                  │  │  RacingLLM    │  │
                                                  │  │  ┌─────────┐  │  │
                                                  │  │  │ Flash   │──┼──┼─► First chunk wins
                                                  │  │  │ Pro     │  │  │
                                                  │  │  └─────────┘  │  │
                                                  │  └───────────────┘  │
                                                  │  ┌───────────────┐  │
                                                  │  │  Tools        │  │
                                                  │  │  • end_call() │  │
                                                  │  └───────────────┘  │
                                                  │  STT: ElevenLabs    │
                                                  │  TTS: ElevenLabs    │
                                                  │  VAD: Silero        │
                                                  └─────────────────────┘

┌─────────────┐
│  FastAPI     │  POST /api/voice/token  →  JWT + agent dispatch
│  (API)       │  GET  /api/voice/health →  status
└─────────────┘
```

**Two processes:**

| Process | Purpose | Entry Point |
|---------|---------|-------------|
| **API Server** | Token generation, agent dispatch | `main.py` (FastAPI + Uvicorn) |
| **Agent Worker** | Voice pipeline (STT → LLM → TTS) | `agent_worker.py` (LiveKit Agents SDK) |

## Racing LLM

The core feature: multiple LLM providers are called simultaneously for every user turn. The first provider to return a streaming chunk is declared the winner — all other providers are cancelled immediately.

- **Providers**: Gemini 2.5 Flash + Gemini 2.5 Pro (configurable)
- **Strategy**: First-chunk-wins with async task cancellation
- **Timeout**: 30 seconds per race
- **Logging**: Winner and provider errors are logged via structlog

Check `services/voice_agent/agent/racing_llm.py` for the implementation.

## Quick Start

### Prerequisites

- Python 3.11+
- A self-hosted [LiveKit server](https://docs.livekit.io/home/self-hosting/local/) or LiveKit Cloud
- API keys for: LiveKit, ElevenLabs, Google Gemini

### Setup

```bash
# Create virtual environment and install dependencies
make setup
source .venv/bin/activate

# Copy and fill in your API keys
cp .env.example .env   # or create .env manually
```

### Environment Variables

Create a `.env` file:

```env
LIVEKIT_ENDPOINT=wss://your-livekit-server.example.com
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
ELEVENLABS_KEY=your_elevenlabs_api_key
GEMINI_KEY=your_google_gemini_api_key
```

### Run

```bash
# Terminal 1 — API server
make run-api

# Terminal 2 — Agent worker
make run-agent

# Or run both together
make run-all
```

### Test

```bash
# Verify API endpoints
make test-api

# Open LiveKit playground for voice testing
make open-playground
```

In the playground:
1. Click **Manual** tab
2. Paste the LiveKit URL and token from `make test-token` output
3. Click **Connect**
4. Speak into your mic — the agent responds via voice

## Docker

```bash
docker compose up -d --build    # Start both services
docker compose down              # Stop
```

## Project Structure

```
voiceagent/
├── main.py                  # FastAPI app entry point
├── agent_worker.py          # LiveKit agent worker entry point
├── config/
│   └── settings.py          # Pydantic settings (env-based)
├── pkg/
│   ├── logger/              # structlog configuration
│   └── error_handling/      # Exception hierarchy + FastAPI handlers
└── services/
    └── voice_agent/
        ├── routes.py        # API endpoints
        ├── service.py       # Token generation + agent dispatch
        ├── constants.py     # Model names, agent config
        ├── ios.py           # LLM provider interface (ABC)
        └── agent/
            ├── voice_agent.py      # Custom Agent with llm_node override
            ├── racing_llm.py       # First-chunk-wins race coordinator
            ├── llm_providers.py    # Gemini provider implementation
            └── pipeline_factory.py # Agent + session assembly
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/voice/token` | Generate a LiveKit room token and dispatch the agent |
| `GET` | `/api/voice/health` | Health check |

### POST /api/voice/token

**Request:**
```json
{
  "room_name": "my-room",
  "participant_name": "user1"
}
```

**Response:**
```json
{
  "token": "eyJ...",
  "livekit_url": "wss://your-server.example.com",
  "room_name": "my-room"
}
```

## Adding an LLM Provider

1. Implement `LLMProviderInterface` in `services/voice_agent/ios.py`:

```python
class MyProvider(LLMProviderInterface):
    @property
    def name(self) -> str:
        return "my-provider"

    async def stream_chat(self, chat_ctx, tools=None):
        async for chunk in my_llm.stream(chat_ctx):
            yield chunk
```

2. Add it to the providers list in `pipeline_factory.py`:

```python
providers = [
    GeminiLLMProvider(model=GEMINI_FLASH_MODEL, api_key=...),
    MyProvider(...),
]
```

## Makefile Targets

| Target | Description |
|--------|-------------|
| `make setup` | Create venv and install dependencies |
| `make run-api` | Start FastAPI server on port 8000 |
| `make run-agent` | Start agent worker in dev mode |
| `make run-all` | Start both services |
| `make test-api` | Run health + token endpoint tests |
| `make open-playground` | Open LiveKit Agents Playground in browser |
| `make lint` | Run ruff linter |
| `make format` | Run ruff formatter |
| `make docker-up` | Build and start Docker services |
| `make docker-down` | Stop Docker services |

## Tech Stack

- **Framework**: FastAPI + LiveKit Agents SDK 1.4
- **LLM**: Google Gemini (Flash + Pro, racing)
- **STT/TTS**: ElevenLabs
- **VAD**: Silero
- **Config**: Pydantic Settings + python-dotenv
- **Logging**: structlog (JSON in prod, console in dev)
- **Containerization**: Docker + Docker Compose
