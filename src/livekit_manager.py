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
            activation_threshold=0.5,
            min_speech_duration=0.15,
            # 1.2s: matches Deepgram endpointing_ms — tolerates Hinglish intra-sentence pauses
            min_silence_duration=1.2,
        ),
        stt=get_stt(language="hi"),
        llm=get_llm(),
        tts=get_tts(),
        # 8s warmup: covers the full ~6s intro greeting so Aria's own TTS echo
        # cannot trigger a false interruption before the user speaks
        aec_warmup_duration=8.0,
        # Wait full 1.2s of silence before sending to LLM — aligns with Deepgram + Silero
        min_endpointing_delay=1.2,
        # Disable: prevents LLM firing before Silero VAD confirms turn is done
        preemptive_generation=False,
        # 150ms is enough for intentional speech — 600ms was blocking all barge-ins
        min_interruption_duration=0.15,
        # Confirm false interruptions in 1s not 2s, so genuine barge-ins aren't held
        agent_false_interruption_timeout=1.0,
        resume_false_interruption=True,
        turn_handling={
            "interruption": {"enabled": True},
            "endpointing": {"min_delay": 1.2, "max_delay": 5.0},
        },
    )
