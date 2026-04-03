"""
conversation_manager.py -- Conversation state tracking and logging.

Tracks per-session metadata:
  - Conversation ID and start time
  - Turn count with per-turn latency (stt_ms, llm_ms, tts_ms, total_ms)
  - Language switches (with timestamps)
  - Scope violations
  - Per-session latency summary

Logs are written to logs/conversations.jsonl for audit trail.
"""
import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

_LOG_DIR = Path(__file__).parent.parent / "logs"
_LOG_FILE = _LOG_DIR / "conversations.jsonl"


class ConversationManager:
    """
    Tracks state for a single voice call session.

    Usage:
        mgr = ConversationManager()
        mgr.record_turn(role="user", text="...", language="hi", stt_ms=420)
        mgr.record_turn(role="assistant", text="...", language="hi", llm_ms=510, tts_ms=210)
        mgr.record_language_switch("en", "hi")
        mgr.record_scope_violation(topic="pricing", transcript="How much?")
        mgr.close()  # writes final log entry with latency summary
    """

    def __init__(self) -> None:
        self.conversation_id: str = str(uuid.uuid4())
        self.start_time: datetime = datetime.now(timezone.utc)
        self.current_language: str = "en"
        self.language_history: list[str] = ["en"]
        self.current_sentiment: str = "neutral"
        self.sentiment_history: list[str] = []
        self.escalated: bool = False
        self.turn_count: int = 0
        self.language_switch_count: int = 0
        self.scope_violations: list[dict] = []
        self.turns: list[dict] = []

        _LOG_DIR.mkdir(exist_ok=True)
        logger.info("[Conv] Session started  id=%s", self.conversation_id)

    def record_turn(
        self,
        role: str,
        text: str,
        language: str,
        stt_ms: Optional[int] = None,
        llm_ms: Optional[int] = None,
        tts_ms: Optional[int] = None,
        sentiment: str = "neutral",
    ) -> None:
        """
        Record a single conversation turn.

        Args:
            role:     'user' or 'assistant'
            text:     Content of the turn
            language: 'en' or 'hi'
            stt_ms:   Speech-to-text latency in ms (user turns only)
            llm_ms:   LLM generation latency in ms (assistant turns only)
            tts_ms:   TTS synthesis+stream latency in ms (assistant turns only)
        """
        self.turn_count += 1

        entry = {
            "turn": self.turn_count,
            "role": role,
            "text": text,
            "language": language,
            "sentiment": sentiment,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.turns.append(entry)
        logger.debug("[Conv] Turn %d (%s/%s): %r", self.turn_count, role, language, text[:60])

    def record_language_switch(self, from_lang: str, to_lang: str) -> None:
        """Record a language switch event."""
        self.language_switch_count += 1
        self.current_language = to_lang
        self.language_history.append(to_lang)
        logger.info(
            "[Conv] Language switch #%d: %s -> %s",
            self.language_switch_count, from_lang, to_lang,
        )

    def record_scope_violation(self, topic: str, transcript: str) -> None:
        """Record an out-of-scope user query."""
        entry = {
            "topic": topic,
            "transcript": transcript,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.scope_violations.append(entry)
        logger.warning("[Conv] Scope violation  topic=%s  text=%r", topic, transcript[:60])

    def record_escalation(self) -> None:
        """Mark the conversation as requiring human escalation."""
        self.escalated = True
        logger.warning("[Conv] Escalation triggered.")

    def update_last_assistant_latency(self, e2e_ms: int) -> None:
        """
        Backfill a real measured e2e_ms into the most recent assistant turn.

        Called by tts_node when the first audio frame is produced, giving
        the actual transcript-to-first-audio latency for that turn.
        """
        for turn in reversed(self.turns):
            if turn["role"] == "assistant":
                turn["e2e_ms"] = e2e_ms
                logger.info("[Conv] Turn %d e2e_ms=%d", turn["turn"], e2e_ms)
                return

    def update_sentiment(self, sentiment: str) -> None:
        """Update the rolling sentiment state and history."""
        self.current_sentiment = sentiment
        self.sentiment_history.append(sentiment)

    def _build_latency_summary(self) -> dict:
        """Compute aggregate latency statistics across all turns."""
        assistant_totals = [t.get("e2e_ms") for t in self.turns if t["role"] == "assistant" and t.get("e2e_ms") is not None]

        def avg(vals: list) -> Optional[int]:
            return round(sum(vals) / len(vals)) if vals else None

        return {
            "avg_e2e_ms": avg(assistant_totals),
            "max_e2e_ms": max(assistant_totals) if assistant_totals else None,
            "turns_under_1500ms": sum(1 for v in assistant_totals if v < 1500),
            "turns_under_2500ms": sum(1 for v in assistant_totals if v < 2500),
        }

    def close(self) -> None:
        """Write the final conversation summary to the JSONL log file."""
        end_time = datetime.now(timezone.utc)
        duration_s = (end_time - self.start_time).total_seconds()

        summary = {
            "conversation_id": self.conversation_id,
            "start_time": self.start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": round(duration_s, 1),
            "turn_count": self.turn_count,
            "language_switches": self.language_switch_count,
            "language_history": self.language_history,
            "scope_violations": self.scope_violations,
            "escalated": self.escalated,
            "latency_summary": self._build_latency_summary(),
            "turns": self.turns,
        }

        try:
            with _LOG_FILE.open("a", encoding="utf-8") as f:
                f.write(json.dumps(summary, ensure_ascii=False) + "\n")
            logger.info(
                "[Conv] Session closed  id=%s  turns=%d  duration=%.1fs",
                self.conversation_id, self.turn_count, duration_s,
            )
        except OSError as exc:
            logger.error("[Conv] Failed to write log: %s", exc)
