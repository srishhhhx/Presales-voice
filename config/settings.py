"""
settings.py — centralised environment variable loader for all modules.

All modules import from here rather than calling os.getenv() directly.
This ensures a single load_dotenv() call and one place to audit all config.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# -- LiveKit
LIVEKIT_URL: str = os.getenv("LIVEKIT_URL", "ws://localhost:7880")
LIVEKIT_API_KEY: str = os.getenv("LIVEKIT_API_KEY", "devkey")
LIVEKIT_API_SECRET: str = os.getenv("LIVEKIT_API_SECRET", "secret")

# -- Speech-to-Text
DEEPGRAM_API_KEY: str | None = os.getenv("DEEPGRAM_API_KEY")

# -- LLM
GROQ_API_KEY: str | None = os.getenv("GROQ_API_KEY")

# -- TTS (AWS Polly primary via livekit-plugins-aws)
AWS_REGION: str = os.getenv("AWS_DEFAULT_REGION", "ap-south-1")

# -- App
LOG_DIR: str = os.getenv("LOG_DIR", "./logs")
SCENARIO: str = os.getenv("SCENARIO", "presale")
