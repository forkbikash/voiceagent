"""Voice agent constants."""

AGENT_INSTRUCTIONS = (
    "You are a helpful voice assistant. Be concise and conversational. "
    "Respond naturally as if speaking to someone. Keep answers brief unless "
    "asked for detail. When the user says goodbye, wants to end the call, "
    "or says they are done, use the end_call tool to hang up."
)

GEMINI_FLASH_MODEL = "gemini-2.5-flash"
GEMINI_PRO_MODEL = "gemini-2.5-pro"

ROOM_PREFIX = "interview-"

AGENT_NAME = "voiceagent_dev"

DEFAULT_TTS_VOICE = "alloy"
