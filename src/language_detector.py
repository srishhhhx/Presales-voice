"""
language_detector.py — parse Deepgram native language tags into session language codes.

No langdetect library. No custom confidence thresholds. Tag parsing only.
Deepgram's detect_language=True returns a language tag on every utterance --
this module normalises it to 'en' or 'hi' for use throughout the pipeline.
"""

SUPPORTED_LANGUAGES: set[str] = {"en", "hi"}


def parse_deepgram_language(deepgram_tag: str | None) -> str:
    """
    Normalise a Deepgram detect_language tag to 'en' or 'hi'.

    Deepgram returns tags like: 'en', 'en-IN', 'hi', 'hi-IN'.
    Splits on '-', takes the base code, and defaults to 'en' on
    missing, empty, or unsupported tags -- never switches without
    a confirmed tag.

    Args:
        deepgram_tag: Language code string from Deepgram STT response,
                      or None if the tag is absent.

    Returns:
        'en' or 'hi'. Always returns a valid session language code.

    Examples:
        >>> parse_deepgram_language('hi-IN')
        'hi'
        >>> parse_deepgram_language('en')
        'en'
        >>> parse_deepgram_language(None)
        'en'
        >>> parse_deepgram_language('fr')
        'en'
    """
    if not deepgram_tag:
        return "en"
    base = deepgram_tag.split("-")[0].lower()
    return base if base in SUPPORTED_LANGUAGES else "en"


def language_switched(new_lang: str, current_lang: str) -> bool:
    """
    Return True if the detected language differs from the current session language.

    Used to decide whether to update ConversationState.current_language
    and swap the TTS voice for the next response.

    Args:
        new_lang: Language code just detected from Deepgram tag ('en' or 'hi').
        current_lang: Current session language stored in ConversationState.

    Returns:
        True if a language switch has occurred, False otherwise.
    """
    return new_lang != current_lang
