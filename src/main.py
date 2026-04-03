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
import time
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
import yaml
from livekit.agents.voice import Agent, ModelSettings
from livekit.plugins import aws, openai, silero

import re
from src.conversation_manager import ConversationManager
from src.livekit_manager import build_session, connect_room
from src.scope_validator import check_scope
from src.language_detector import detect_language_combined
from src.stt_engine import get_stt
from src.tts_engine import get_tts
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize local VADER lexicon engine once
_sentiment_analyzer = SentimentIntensityAnalyzer()

def detect_sentiment(text: str) -> str:
    """Analyze string sentiment securely in memory (~1ms zero latency)"""
    scores = _sentiment_analyzer.polarity_scores(text)
    if scores['compound'] >= 0.05:
        return "positive"
    elif scores['compound'] <= -0.05:
        return "negative"
    return "neutral"

# Load structured YAML system prompt from config
_PROMPT_PATH = Path(__file__).parent.parent / "config" / "prompts" / "presale_system_prompt.yaml"
try:
    with open(_PROMPT_PATH, "r", encoding="utf-8") as f:
        _prompt_parsed = yaml.safe_load(f)
        _SYSTEM_PROMPT = "You are an AI adhering strictly to the following configuration:\n\n" + yaml.dump(_prompt_parsed, sort_keys=False, allow_unicode=True)
except Exception as e:
    logger.warning("Could not load YAML prompt, defaulting. Error: %s", e)
    _SYSTEM_PROMPT = "You are Aria, a presales assistant."


class PresalesAgent(Agent):
    """
    Aria -- VoiceFlow AI presales agent.

    stt_node : Single Nova-2 hi stream -- handles EN, HI, Hinglish with no restarts.
    tts_node : Aditi (standard) -- Indian English and Hindi voice.
    Scope    : Every transcript checked; out-of-scope triggers log + LLM redirect.
    Conv     : ConversationManager tracks turns, language switches, scope violations.
    """

    def __init__(self) -> None:
        super().__init__(instructions=_SYSTEM_PROMPT)
        self.conv = ConversationManager()
        # Monotonic timestamp set when a user transcript arrives.
        # Used to compute real e2e latency (transcript → first TTS byte).
        self._transcript_ts: float | None = None

    async def stt_node(
        self,
        audio: AsyncIterable[rtc.AudioFrame],
        model_settings: ModelSettings,
    ) -> AsyncIterable[stt.SpeechEvent]:
        """
        Single Nova-2 language=hi stream for the full session.
        Handles EN, HI and Hinglish without stream restarts.
        Logs every transcript + scope check result.
        On WebSocket/Deepgram error, yields a graceful fallback transcript.
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
                            lang = detect_language_combined(text, dg_tag)
                            if lang != self.conv.current_language:
                                self.conv.record_language_switch(self.conv.current_language, lang)
                            # Mark transcript arrival time for e2e measurement.
                            self._transcript_ts = time.monotonic()
                            
                            # 1. Zero-latency Sentiment check
                            sentiment = detect_sentiment(text)
                            self.conv.update_sentiment(sentiment)

                            # 2. Dynamic Tone instruction mutation
                            base_instructions = _SYSTEM_PROMPT
                            if sentiment == "negative":
                                tone_injection = "\n\n[SYSTEM NOTE] The user sounds frustrated or negative. Be extra empathetic, patient, and softly apologetic."
                                self._instructions = base_instructions + tone_injection
                            elif sentiment == "positive":
                                tone_injection = "\n\n[SYSTEM NOTE] The user sounds positive. Match their energy warmly and be slightly more upbeat!"
                                self._instructions = base_instructions + tone_injection
                            else:
                                self._instructions = base_instructions
                            
                            
                            if not in_scope:
                                self.conv.record_scope_violation(topic=topic, transcript=text)
                                logger.warning("[SCOPE] topic=%s  transcript=%r", topic, text)
                            else:
                                if any(phrase in text.lower() for phrase in ["human", "agent", "customer service", "escalate", "representative", "operator"]):
                                    self.conv.record_escalation()
                                self.conv.record_turn(role="user", text=text, language=lang, sentiment=sentiment)
                                logger.info("[STT] transcript=%r  dg_tag=%s sentiment=%s", text, dg_tag, sentiment)

                            # 3. Dynamic language injection so LLM always responds in the right language
                            lang_label = "Hindi" if lang == "hi" else "English"
                            lang_note = f"\n\n[LANGUAGE] The user's last message was in {lang_label}. You MUST respond entirely in {lang_label}."
                            self._instructions = self._instructions + lang_note

                    yield event
            except Exception as exc:
                # Catches WebSocket drops, Deepgram timeouts, or auth errors.
                # Yield a graceful fallback so the LLM can respond rather than crash.
                logger.error("[STT] Stream error: %s", exc, exc_info=True)
                yield stt.SpeechEvent(
                    type=stt.SpeechEventType.FINAL_TRANSCRIPT,
                    alternatives=[
                        stt.SpeechData(
                            text="Sorry, I didn't catch that. Could you please repeat?",
                            language="en-IN",
                            confidence=0.0,
                            start_time=0.0,
                            end_time=0.0,
                        )
                    ],
                )
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
            assistant_full_text = []
            async def forward_text() -> None:
                async for chunk in text:
                    chunk = re.sub(r'[^\u0900-\u097Fa-zA-Z0-9\s.,!?"\'-]', '', chunk)
                    if chunk:
                        assistant_full_text.append(chunk)
                        stream.push_text(chunk)
                stream.end_input()
                full_trans = "".join(assistant_full_text).strip()
                if full_trans:
                    self.conv.record_turn(role="assistant", text=full_trans, language=self.conv.current_language)
                    logger.info("[Agent] Speech committed: %r", full_trans[:60])

            forward_task = asyncio.create_task(forward_text())
            _first_frame = True
            try:
                async for ev in stream:
                    if _first_frame:
                        # Real e2e: time from user transcript → first audio byte out.
                        if self._transcript_ts is not None:
                            e2e_ms = round((time.monotonic() - self._transcript_ts) * 1000)
                            self.conv.update_last_assistant_latency(e2e_ms=e2e_ms)
                            logger.info("[METRICS] e2e_ms=%d", e2e_ms)
                            self._transcript_ts = None
                        _first_frame = False
                    yield ev.frame
            finally:
                forward_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await forward_task


async def entrypoint(ctx: JobContext) -> None:
    """LiveKit agent entrypoint -- initialises Aria for a new call."""
    await connect_room(ctx)

    agent = PresalesAgent()
    session = build_session()

    await session.start(agent=agent, room=ctx.room)

    # Wait for the first participant to join before greeting.
    # This ensures AEC warmup fully settles before Aria starts speaking,
    # preventing her own TTS echo from triggering a false interruption mid-intro.
    participant = await ctx.wait_for_participant()
    logger.info("[Agent] Participant joined: %s — starting greeting", participant.identity)

    await session.generate_reply(
        instructions=(
            "Introduce yourself as Aria from VoiceFlow AI in one sentence. "
            "Say you're here to understand their business and see if VoiceFlow can help. "
            "Then ask one warm opening question: what kind of business they run or what brings them here today."
        )
    )
    logger.info("[Agent] Aria ready")

    @ctx.room.on("disconnected")
    def on_disconnected(*args, **kwargs):
        """Ensure logs write to JSONL on call end."""
        logger.info("[Agent] Call ended, flushing logs...")
        agent.conv.close()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
