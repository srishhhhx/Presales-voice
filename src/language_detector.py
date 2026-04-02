"""
language_detector.py -- Detect session language from Deepgram utterance tags.

Primary detection: Deepgram language tag (event.alternatives[0].language)
  In Nova-2 multi mode, Deepgram returns a per-utterance language code
  like 'en', 'hi', 'en-IN', 'hi-IN'. This is the most reliable signal
  and enables seamless automatic language switching.

Fallback detection (when language tag is absent/None):
  1. Devanagari Unicode characters (U+0900-U+097F) -- pure Hindi
  2. Explicit intent phrases -- 'in hindi', 'in english', etc.

Removed: single-word Hinglish keyword heuristic.
  Individual Hindi words like 'baat', 'kya', 'haan' caused false positives
  when the STT misread English speech (e.g. 'what' → 'baat').
"""

SUPPORTED_LANGUAGES: set[str] = {"en", "hi"}

# Explicit Hindi switch intent -- detected reliably in English sentences
SWITCH_TO_HINDI_PHRASES: tuple[str, ...] = (
    "in hindi",
    "speak hindi",
    "switch to hindi",
    "change to hindi",
    "hindi mein",
    "hindi me",
)

# Explicit English switch intent.
# Include common hi-model mishearings of "switch to English":
#   "switch to English" → "suits do English", "switch the English", etc.
SWITCH_TO_ENGLISH_PHRASES: tuple[str, ...] = (
    "in english",
    "speak english",
    "switch to english",
    "change to english",
    "switch the english",
    "suits do english",
    "suits to english",
    "now english",
    "do english",
)


def detect_language_from_tag(deepgram_language_tag: str | None) -> str | None:
    """
    Parse Deepgram's per-utterance language tag to 'en' or 'hi'.

    In Nova-2 multi mode, Deepgram returns a language code per utterance
    (e.g. 'en', 'hi', 'en-IN', 'hi-IN'). This is the primary and most
    reliable language detection signal -- use this before falling back
    to text analysis.

    Args:
        deepgram_language_tag: Language code from event.alternatives[0].language.
                               May be None if not present in the response.

    Returns:
        'en', 'hi', or None if the tag is absent or unrecognised.
    """
    if not deepgram_language_tag:
        return None
    base = deepgram_language_tag.split("-")[0].lower()
    return base if base in SUPPORTED_LANGUAGES else None


def detect_language_from_transcript(text: str) -> str:
    """
    Text-only fallback language detection.

    Priority order:
      1. Explicit English switch phrase ('in english', 'switch to english')
      2. Explicit Hindi switch phrase  ('in hindi',  'switch to hindi')
      3. Devanagari Unicode characters  (unambiguous pure Hindi)
      4. Default: 'en'

    Single Hindi keywords are intentionally excluded -- they cause false
    positives (e.g. keyword boost turning 'what' into 'baat').

    Args:
        text: Transcript text from Deepgram STT.

    Returns:
        'hi' or 'en'.
    """
    if not text or not text.strip():
        return "en"

    text_lower = text.lower()

    # Explicit English switch (check before Hindi to avoid misclassification)
    if any(phrase in text_lower for phrase in SWITCH_TO_ENGLISH_PHRASES):
        return "en"

    # Explicit Hindi switch
    if any(phrase in text_lower for phrase in SWITCH_TO_HINDI_PHRASES):
        return "hi"

    # Devanagari script -- pure Hindi
    if any("\u0900" <= ch <= "\u097f" for ch in text):
        return "hi"

    return "en"


def detect_language_combined(text: str, dg_tag: str | None) -> str:
    """
    Unified language detection combining text analysis and DG tag.

    Priority order -- designed so that explicit user intent always wins:
      1. Explicit English switch phrase in text
         ('switch to english', 'in english')  -- user stated intent clearly
      2. Explicit Hindi switch phrase in text
         ('switch to hindi', 'in hindi', 'hindi mein')
      3. Devanagari Unicode characters in text (pure Hindi speech)
      4. Deepgram's per-utterance language tag  (dg_tag, reliable for speech)
      5. Default: 'en'

    The Deepgram tag is placed AFTER explicit phrases because the tag is set
    by the acoustic model and cannot know the user's code-switching intent.
    Example: 'Switch to Hindi' → dg_tag='en-IN', text='hi' → correct: 'hi'.

    Args:
        text:   Transcript text from the current utterance.
        dg_tag: Deepgram per-utterance language code (may be None).

    Returns:
        'hi' or 'en'.
    """
    if not text or not text.strip():
        return "en"

    text_lower = text.lower()

    # 1. Explicit English intent always wins
    if any(phrase in text_lower for phrase in SWITCH_TO_ENGLISH_PHRASES):
        return "en"

    # 2. Explicit Hindi intent always wins
    if any(phrase in text_lower for phrase in SWITCH_TO_HINDI_PHRASES):
        return "hi"

    # 3. Devanagari script (unambiguous -- hi STT returns this for pure Hindi)
    if any("\u0900" <= ch <= "\u097f" for ch in text):
        return "hi"

    # 4. Deepgram's acoustic language tag (most reliable for non-explicit speech)
    tag = detect_language_from_tag(dg_tag)
    if tag is not None:
        return tag

    # 5. Default
    return "en"


def language_switched(new_lang: str, current_lang: str) -> bool:
    """Return True if the detected language differs from the current one."""
    return new_lang != current_lang
