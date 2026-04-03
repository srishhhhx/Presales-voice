"""
test_stt.py -- Deepgram STT configuration tests.

Ensures the factory configures the models and languages correctly
before connecting to the websocket.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / ".env")
except ImportError:
    pass

from src.stt_engine import get_stt


def test_stt_english_default():
    """Fallback English configuration sets lang and defaults correctly."""
    stt = get_stt()
    assert stt._opts.language == "en-IN"
    assert stt._opts.model == "nova-3"
    assert stt._opts.punctuate is True


def test_stt_hindi():
    """Primary STT must use nova-2 for streaming Hindi+English bilingual support."""
    stt = get_stt(language="hi")
    assert stt._opts.language == "hi"
    assert stt._opts.model == "nova-2"
    assert stt._opts.punctuate is True


def test_stt_options_validation():
    """STT options must disable smart smart_format for hindi if unsupported, 
    but for now smart_format is explicitly True in factory."""
    stt = get_stt("en")
    assert getattr(stt._opts, "interim_results", None) is False
    assert getattr(stt._opts, "smart_format", None) is True
