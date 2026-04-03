"""
livekit_manager.py -- LiveKit room connection and session configuration.

Centralises all LiveKit-specific setup so main.py stays thin.
"""
import os
import logging
from livekit.agents import (
    AgentSession,
    AutoSubscribe,
    JobContext,
    TurnHandlingOptions,
)
from livekit.plugins import silero

from src.llm_processor import get_llm
from src.tts_engine import get_tts
from src.stt_engine import get_stt

logger = logging.getLogger(__name__)


async def connect_room(ctx: JobContext) -> None:
    """Connect to the LiveKit room, subscribing to audio only."""
    logger.info("[LiveKit] Connecting to room: %s", ctx.room.name)
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    logger.info("[LiveKit] Connected")


def build_session() -> AgentSession:
    """
    Build and return a fully configured AgentSession.

    Components:
      - VAD  : Silero voice activity detection
      - STT  : Deepgram Nova-2 language=hi (EN + HI + Hinglish)
      - LLM  : Groq llama-3.3-70b-versatile
      - TTS  : AWS Polly Aditi standard (Indian accent)
    """
    return AgentSession(
        vad=silero.VAD.load(
            activation_threshold=0.3,
            min_speech_duration=0.01,
            min_silence_duration=0.8,
        ),
        stt=get_stt(language="hi"),
        llm=get_llm(),
        tts=get_tts(),
        turn_handling=TurnHandlingOptions(interruption={"enabled": True}),
    )
