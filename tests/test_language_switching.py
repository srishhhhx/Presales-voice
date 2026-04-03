"""
test_language_switching.py -- Unit tests for language detection logic.

Tests Deepgram tag parsing, switch detection, and edge cases.
Run with: pytest tests/test_language_switching.py -v
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.language_detector import detect_language_combined


# ── Deepgram tag parsing ──────────────────────────────────────────────────────

def test_hindi_tag_detected():
    # Use non-empty text so the dg_tag lookup is reached (empty text defaults to 'en')
    assert detect_language_combined(text="acha", dg_tag="hi") == "hi"


def test_hindi_in_tag_detected():
    assert detect_language_combined(text="haan", dg_tag="hi-IN") == "hi"


def test_english_tag_detected():
    assert detect_language_combined(text="Hello, how are you?", dg_tag="en") == "en"


def test_english_in_tag_detected():
    assert detect_language_combined(text="", dg_tag="en-IN") == "en"


def test_missing_tag_defaults_to_english():
    assert detect_language_combined(text="Hello there", dg_tag=None) == "en"


def test_empty_tag_defaults_to_english():
    assert detect_language_combined(text="Hello world", dg_tag="") == "en"


def test_unsupported_tag_defaults_to_english():
    assert detect_language_combined(text="Bonjour", dg_tag="fr") == "en"


# ── Explicit switch phrase detection ─────────────────────────────────────────

def test_explicit_english_switch_phrase():
    """User says 'switch to english' — must override dg_tag=hi."""
    lang = detect_language_combined(text="please switch to english", dg_tag="hi")
    assert lang == "en"


def test_explicit_hindi_switch_phrase():
    """User says 'hindi mein baat karo' — must override dg_tag=en."""
    lang = detect_language_combined(text="hindi mein baat karo", dg_tag="en")
    assert lang == "hi"


# ── Devanagari script detection ───────────────────────────────────────────────

def test_devanagari_script_detected_as_hindi():
    lang = detect_language_combined(
        text="हमारी क्लिनिक में रोज़ दो सौ कॉल आती हैं",
        dg_tag=None,
    )
    assert lang == "hi"


def test_devanagari_overrides_missing_tag():
    lang = detect_language_combined(text="आपका स्वागत है", dg_tag="")
    assert lang == "hi"


# ── Hinglish / mixed ─────────────────────────────────────────────────────────

def test_hinglish_uses_dg_tag_as_tiebreaker():
    """When Hinglish is spoken, Deepgram tag is the tiebreaker."""
    lang = detect_language_combined(
        text="I get around 200 calls, but kaafi manual ho jata hai",
        dg_tag="hi",
    )
    assert lang == "hi"


def test_english_dominant_hinglish_with_en_tag():
    lang = detect_language_combined(
        text="We handle calls mostly in the morning, thoda busy hota hai",
        dg_tag="en",
    )
    assert lang == "en"
