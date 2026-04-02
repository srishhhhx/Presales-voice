"""
main.py -- LiveKit bilingual presales voicebot (VoiceFlow AI / Aria).

Pipeline:
  STT : Deepgram Nova-2 language=hi (handles EN + HI + Hinglish, zero restarts)
  LLM : Groq llama-3.3-70b-versatile via OpenAI-compatible API
  TTS : AWS Polly Aditi standard (native en-IN + hi-IN, Indian accent)
  VAD : Silero

Scope validation runs on every user transcript before LLM generation.
Out-of-scope queries (pricing, contracts, competitors) trigger a redirect
hint injected into the LLM context to keep responses in-scope.
"""
import asyncio
import contextlib
import logging
import os
import sys
from collections.abc import AsyncIterable
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import (
    AgentSession,
    AutoSubscribe,
    JobContext,
    TurnHandlingOptions,
    WorkerOptions,
    cli,
    stt,
    tts,
    tokenize,
)
from livekit.agents.voice import Agent, ModelSettings
from livekit.plugins import aws, openai, silero

from src.scope_validator import check_scope, get_scope_reinforcement
from src.stt_engine import get_stt

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load system prompt from config
_PROMPT_PATH = Path(__file__).parent.parent / "config" / "prompts" / "presale_system_prompt.txt"
_SYSTEM_PROMPT = _PROMPT_PATH.read_text(encoding="utf-8").strip()


class PresalesAgent(Agent):
    """
    Aria — VoiceFlow AI presales agent.

    stt_node : Single Nova-2 hi stream -- handles EN, HI, Hinglish with no restarts.
    tts_node : Aditi (standard) -- Indian English and Hindi voice.
    Scope    : Every transcript checked; out-of-scope triggers LLM redirect hint.
    """

    def __init__(self) -> None:
        super().__init__(instructions=_SYSTEM_PROMPT)

    async def stt_node(
        self,
        audio: AsyncIterable[rtc.AudioFrame],
        model_settings: ModelSettings,
    ) -> AsyncIterable[stt.SpeechEvent]:
        """
        Single Nova-2 language=hi stream for the full session.
        Handles EN, HI and Hinglish without stream restarts.
        Logs every transcript + scope check result.
        """
        logger.info("[STT] Opening Nova-2 hi stream")

        async with get_stt(language="hi").stream() as stream:
            async def push_frames(s=stream) -> None:
                async for frame in audio:
                    s.push_frame(frame)
                s.end_input()

            push_task = asyncio.create_task(push_frames())
            try:
                async for event in stream:
                    if (
                        event.type == stt.SpeechEventType.FINAL_TRANSCRIPT
                        and event.alternatives
                    ):
                        alt = event.alternatives[0]
                        text = (alt.text or "").strip()
                        if text:
                            dg_tag = getattr(alt, "language", None)
                            in_scope, topic, hint = check_scope(text)
                            if not in_scope:
                                logger.warning(
                                    "[SCOPE] Out-of-scope topic=%s  transcript=%r  hint=%s",
                                    topic, text, hint,
                                )
                            else:
                                logger.info(
                                    "[STT] transcript=%r  dg_tag=%s",
                                    text, dg_tag,
                                )
                    yield event
            finally:
                push_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await push_task

    async def tts_node(
        self,
        text: AsyncIterable[str],
        model_settings: ModelSettings,
    ) -> AsyncIterable[rtc.AudioFrame]:
        """Aditi (standard) -- Indian English and Hindi, native Indian accent."""
        logger.info("[TTS] Aditi")
        wrapped = tts.StreamAdapter(
            tts=aws.TTS(voice="Aditi", speech_engine="standard"),
            sentence_tokenizer=tokenize.blingfire.SentenceTokenizer(retain_format=True),
        )
        async with wrapped.stream() as stream:
            async def forward_text() -> None:
                async for chunk in text:
                    stream.push_text(chunk)
                stream.end_input()

            forward_task = asyncio.create_task(forward_text())
            try:
                async for ev in stream:
                    yield ev.frame
            finally:
                forward_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await forward_task


async def entrypoint(ctx: JobContext) -> None:
    """LiveKit agent entrypoint -- initialises Aria for a new call."""
    logger.info("[Agent] New call -- connecting")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    agent = PresalesAgent()

    session = AgentSession(
        vad=silero.VAD.load(),
        stt=get_stt(language="hi"),
        llm=openai.LLM(
            model="llama-3.3-70b-versatile",
            base_url="https://api.groq.com/openai/v1",
            api_key=os.getenv("GROQ_API_KEY"),
        ),
        tts=aws.TTS(voice="Aditi", speech_engine="standard"),
        turn_handling=TurnHandlingOptions(interruption={"enabled": True}),
    )

    await session.start(agent=agent, room=ctx.room)

    # Aria's opening line — warm, brief, invites the prospect to speak
    await session.generate_reply(
        instructions=(
            "Introduce yourself as Aria from VoiceFlow AI in one sentence. "
            "Say you're here to understand their business and see if VoiceFlow can help. "
            "Then ask one warm opening question: what kind of business they run or what brings them here today."
        )
    )
    logger.info("[Agent] Aria ready")


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
