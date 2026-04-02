"""
stt_engine.py — Deepgram STT configuration factory for the LiveKit AgentSession.

Provides a factory function that returns a correctly configured deepgram.STT
plugin instance for use in AgentSession(stt=...). Key settings:
  - nova-2 model: highest accuracy for English and Hindi
  - detect_language=True: native EN/HI tag on every utterance, zero extra API call
  - Hindi keyword boosting for improved accuracy on common terms
"""
import os
from livekit.plugins import deepgram


# Hindi terms to boost in Deepgram's recognition model.
# Format: "word:boost_factor" -- 2x weight on these tokens.
HINDI_KEYWORDS: list[str] = [
    "namaste:2",
    "haan:2",
    "theek:2",
    "aapka:2",
    "kaise:2",
    "accha:2",
    "bilkul:2",
    "dhanyawad:2",
]


def get_stt() -> deepgram.STT:
    """
    Return a configured Deepgram STT plugin instance for AgentSession.

    Configuration choices:
      - model='nova-2': best accuracy for Indian English and Hindi
      - detect_language=True: returns 'en'/'hi'/'en-IN'/'hi-IN' tag on
        every utterance, parsed by language_detector.parse_deepgram_language()
      - keywords: boosts common Hindi terms to improve recognition accuracy
      - language parameter is NOT set -- detect_language handles this natively

    Returns:
        deepgram.STT: configured STT plugin ready for AgentSession(stt=...).
    """
    return deepgram.STT(
        model="nova-2",
        detect_language=True,
        keywords=HINDI_KEYWORDS,
    )


def get_language_tag_from_result(result: object) -> str | None:
    """
    Extract the Deepgram language tag from a transcript result object.

    Deepgram returns the detected language at:
      result.channel.alternatives[0].language

    This is available on every utterance when detect_language=True is set.
    No additional API call required -- included in STT response.

    Args:
        result: Deepgram transcript result object from the STT callback.

    Returns:
        Language tag string (e.g. 'hi', 'en-IN') or None if absent.
    """
    try:
        return result.channel.alternatives[0].language
    except (AttributeError, IndexError):
        return None
