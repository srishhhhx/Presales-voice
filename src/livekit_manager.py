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
            # Raised from 0.3 → 0.5: prevents TTS echo from registering as user speech
            activation_threshold=0.5,
            # Raised from 0.01 → 0.15: ignores sub-150ms noise blips / breathing
            min_speech_duration=0.15,
            # Keep at 0.8s to allow natural mid-sentence pauses
            min_silence_duration=0.8,
        ),
        stt=get_stt(language="hi"),
        llm=get_llm(),
        tts=get_tts(),
        # Align session-level endpointing with Deepgram's 800ms endpointing_ms
        min_endpointing_delay=0.8,
        # Allow genuine barge-ins but require 600ms of sustained speech to count
        min_interruption_duration=0.6,
        # Auto-resume if the framework determines the interruption was a false positive
        resume_false_interruption=True,
        turn_handling={
            "interruption": {"enabled": True},
            "endpointing": {"min_delay": 0.8, "max_delay": 4.0},
        },
    )
