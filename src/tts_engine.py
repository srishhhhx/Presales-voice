"""
tts_engine.py -- AWS Polly TTS configuration and factory.

Voice: Aditi (standard engine)
  - Native Indian English (en-IN) and Hindi (hi-IN) support
  - Consistent voice across both languages -- no jarring switches
  - Standard engine selected for widest language coverage
    (neural engine does not support hi-IN for Aditi)
"""
import logging
from livekit.plugins import aws

logger = logging.getLogger(__name__)

_DEFAULT_VOICE = "Aditi"
_DEFAULT_ENGINE = "standard"


def get_tts(voice: str = _DEFAULT_VOICE, engine: str = _DEFAULT_ENGINE) -> aws.TTS:
    """
    Return a configured AWS Polly TTS instance.

    Args:
        voice : Polly voice ID. Default: Aditi (Indian English + Hindi).
        engine: Speech engine. Default: standard (required for hi-IN support).

    Returns:
        Configured aws.TTS instance.
    """
    logger.debug("[TTS] voice=%s engine=%s", voice, engine)
    return aws.TTS(voice=voice, speech_engine=engine)
