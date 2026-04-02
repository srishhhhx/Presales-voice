"""
scope_validator.py -- Validates LLM responses and user queries against presale scope.

Detects out-of-scope topics (pricing, contracts, competitors) from the user's
input so the LLM system prompt can be reinforced dynamically, and provides
a lightweight check that can be used for logging scope violations.
"""
import re

# Keywords that indicate out-of-scope user intent
_OUT_OF_SCOPE_PATTERNS: list[tuple[str, str]] = [
    # (topic_key, regex pattern)
    ("pricing",     r"\b(price|pricing|cost|costs|quote|rupee|rs\.?|inr|how much|kitna|lagega|charge)\b"),
    ("discount",    r"\b(discount|offer|deal|kam karo|negotiate|cheaper)\b"),
    ("contract",    r"\b(contract|sla|agreement|terms|legal|clause)\b"),
    ("timeline",    r"\b(how (long|soon)|implementation time|deploy|kitne din|kab tak|deadline)\b"),
    ("competitor",  r"\b(vs\.?|versus|better than|compare|twilio|exotel|knowlarity|servetel)\b"),
]

_OUT_OF_SCOPE_HINTS = {
    "pricing":    "Pricing is customised — our product team will cover this in detail during the demo.",
    "discount":   "Discount structures are handled by our sales team directly.",
    "contract":   "Contract details are best discussed with our sales team.",
    "timeline":   "Implementation timelines depend on your setup — our team will give a realistic estimate in the demo.",
    "competitor": "I'd prefer to focus on how VoiceFlow fits your needs specifically.",
}


def check_scope(text: str) -> tuple[bool, str | None, str | None]:
    """
    Check whether user text contains out-of-scope keywords.

    Args:
        text: Transcript text from the user.

    Returns:
        (in_scope, topic, redirect_hint)
        - in_scope: True if no out-of-scope topic detected
        - topic: matched topic key, or None
        - redirect_hint: suggested redirect sentence, or None
    """
    text_lower = text.lower()
    for topic, pattern in _OUT_OF_SCOPE_PATTERNS:
        if re.search(pattern, text_lower):
            return False, topic, _OUT_OF_SCOPE_HINTS[topic]
    return True, None, None


def get_scope_reinforcement(topic: str) -> str:
    """
    Return a one-sentence system reinforcement to prepend to the LLM context
    when an out-of-scope topic is detected. Keeps the LLM anchored.
    """
    return (
        f"IMPORTANT: The user just asked about {topic}. "
        f"Do NOT provide any information about {topic}. "
        f"Use this redirect: \"{_OUT_OF_SCOPE_HINTS.get(topic, 'I cannot discuss that directly.')}\""
    )
