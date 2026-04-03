import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.main import detect_sentiment

def test_negative_sentiment_detected():
    """Ensure VADER categorizes explicitly frustrated phrasing as negative."""
    assert detect_sentiment("This is incredibly frustrating, nothing is working at all") == "negative"

def test_positive_sentiment_detected():
    """Ensure VADER categorizes happy phrasing as positive."""
    assert detect_sentiment("This sounds absolutely great, I love it so much") == "positive"

def test_neutral_sentiment_detected():
    """Ensure VADER categorizes general queries as neutral."""
    assert detect_sentiment("Tell me more about your product") == "neutral"
    assert detect_sentiment("how much does it cost") == "neutral"
