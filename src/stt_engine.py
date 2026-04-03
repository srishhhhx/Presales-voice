"""
stt_engine.py -- Deepgram STT configuration factory.

Models:
  English (en-IN): nova-3 -- latest model, strong English accuracy
  Hindi   (hi):    nova-2 -- confirmed streaming support for language=hi
                             nova-3 Hindi streaming support unconfirmed

Keyword boosting is disabled -- causes transcription errors in multi mode.
"""
from livekit.plugins import deepgram

_MODEL_FOR_LANG = {
    "hi":    "nova-2",   # confirmed streaming Hindi support
    "en-IN": "nova-3",   # latest, best English accuracy
}


def get_stt(language: str = "en") -> deepgram.STT:
    """
    Return a single-language Deepgram STT instance.

    language='en' -> nova-3 en-IN
    language='hi' -> nova-2 hi  (nova-2 confirmed for Hindi streaming)
    """
    lang_code = "hi" if language == "hi" else "en-IN"
    model = _MODEL_FOR_LANG[lang_code]
    return deepgram.STT(
        model=model,
        language=lang_code,
        interim_results=False,
        smart_format=True,
        punctuate=True,
        # 1200ms: Indian/Hinglish speakers pause up to ~1.2s mid-sentence
        endpointing_ms=1200,
    )

