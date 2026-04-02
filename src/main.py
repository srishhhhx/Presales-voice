"""
main.py -- LiveKit bilingual presales voicebot.

Architecture (single-stream, no restarts):
  STT: Nova-2 language=hi for the entire session.
       The hi model handles English, Hindi, and Hinglish seamlessly.
       Confirmed from logs: "Pause for a second." → perfect in hi mode.
       No stream restarts = no mid-conversation breakage.

  LLM: Instructed to respond in the language the user speaks each turn.
       Detects Hinglish naturally -- "kaafi manual ho jata hai" → responds HI.
       "can you explain in English?" → responds EN.

  TTS: Aditi (standard) for all speech -- native en-IN and hi-IN.
       No voice switching needed; Aditi handles both.

  Language tracking: used only for LLM context injection, not for stream control.
"""
import asyncio
import contextlib
import logging
import os
import sys
from collections.abc import AsyncIterable

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

from src.stt_engine import get_stt

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PresalesAgent(Agent):
    """
    Bilingual presales agent -- single hi stream, no restarts.

    stt_node: Nova-2 language=hi handles EN, HI, and Hinglish in one
              persistent stream. No language-triggered restarts.
    tts_node: Aditi (standard) for all speech.
    """

    def __init__(self, instructions: str) -> None:
        super().__init__(instructions=instructions)

    async def stt_node(
        self,
        audio: AsyncIterable[rtc.AudioFrame],
        model_settings: ModelSettings,
    ) -> AsyncIterable[stt.SpeechEvent]:
        """
        Single persistent Nova-2 hi stream for the entire session.

        language=hi transcribes:
          - Pure English    e.g. "Hi I'm looking to automate my calls"
          - Pure Hindi      e.g. "तुम्हारा नाम क्या है?"
          - Hinglish        e.g. "kaafi manual ho jata hai" / "200 calls hain"

        No stream restarts means no mid-conversation dead zones.
        The LLM receives the transcript as-is and matches the user's language.
        """
        logger.info("[STT] Opening single hi stream (EN+HI+Hinglish)")

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
        """Aditi (standard) -- handles en-IN and hi-IN natively."""
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
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    agent = PresalesAgent(
        instructions=(
            "You are a helpful bilingual presales assistant supporting English and Hindi. "
            "Carefully read EACH user message and respond ONLY in the language of that message:\n"
            "- If the message is in Hindi or Hinglish (mixed Hindi/English), respond in Hindi.\n"
            "- If the message is in English, respond in English.\n"
            "- If the user asks to explain in English, switch to English immediately.\n"
            "- If the user asks to speak in Hindi, switch to Hindi immediately.\n"
            "Never mix languages in your response. Match the user's language exactly. "
            "Keep responses to 2-3 sentences."
        )
    )

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
    await session.generate_reply(
        instructions=(
            "Greet the user warmly in English. Say you're a bilingual assistant "
            "and will respond naturally in whichever language they use — "
            "English, Hindi, or a mix of both. One sentence only."
        )
    )
    logger.info("[Agent] Ready -- single hi stream active")


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
