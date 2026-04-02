"""
main.py — LiveKit agent entrypoint.

PHASE 1 STUB: Establishes the full AgentSession pipeline with STT, LLM, and TTS.
The agent echoes a simple greeting and listens. Language detection tags are
printed to console to verify Deepgram detect_language=True is working.

Phase 1 verification:
  - Agent starts without error
  - English transcript appears in console/log
  - Hindi transcript appears in console/log
  - Deepgram language tag ('en' or 'hi') visible in output

Run:
  python src/main.py dev
Then open: https://agents-playground.livekit.io
Connect with your LiveKit credentials, speak in English and Hindi.
"""
import os
import sys
import logging

# Add project root to path so config/ is importable from src/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    cli,
    AgentSession,
    TurnHandlingOptions,
)
from livekit.agents.voice import Agent
from livekit.plugins import silero, openai, aws

from src.stt_engine import get_stt
from src.language_detector import parse_deepgram_language

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def entrypoint(ctx: JobContext) -> None:
    """
    LiveKit agent entrypoint. Called once per room connection.

    Initialises AgentSession with:
      - Silero VAD for voice activity detection
      - Deepgram nova-2 STT with detect_language=True
      - Groq llama-3.3-70b-versatile via openai.LLM compatible endpoint
      - AWS Polly Raveena (Indian English) as primary TTS

    Phase 1: Uses a minimal instruction set to verify the pipeline.
    Subsequent phases will load the full presale system prompt.

    Args:
        ctx: LiveKit JobContext providing room and participant access.
    """
    logger.info("Entrypoint called -- connecting to room")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Phase 1 stub instructions -- replaced with full system prompt in Phase 2
    agent = Agent(
        instructions=(
            "You are a helpful assistant. "
            "Keep all responses to one sentence. "
            "If greeted in Hindi, respond in Hindi. "
            "If greeted in English, respond in English."
        )
    )

    session = AgentSession(
        vad=silero.VAD.load(),
        stt=get_stt(),
        llm=openai.LLM(
            model="llama-3.3-70b-versatile",
            base_url="https://api.groq.com/openai/v1",
            api_key=os.getenv("GROQ_API_KEY"),
        ),
        tts=aws.TTS(voice="Raveena", speech_engine="standard"),
        turn_handling=TurnHandlingOptions(interruption={"enabled": True}),
    )

    logger.info("Starting AgentSession in room: %s", ctx.room.name)
    await session.start(agent=agent, room=ctx.room)

    # Initial greeting to confirm the pipeline is live
    await session.generate_reply(
        instructions=(
            "Greet the user briefly. Say you are a test assistant "
            "and ask them to speak in English or Hindi."
        )
    )
    logger.info("Phase 1 pipeline active -- speak to test STT and language detection")


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
