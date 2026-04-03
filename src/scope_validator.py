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
    ("pricing",     r"\b(price|pricing|cost|costs|quote|rupee|rs\.?|inr|how much|rate card|kitna|lagega|charge)\b"),
    ("discount",    r"\b(discount|offer|deal|kam karo|negotiate|cheaper)\b"),
    ("contract",    r"\b(contract|sla|agreement|terms|legal|clause)\b"),
    ("timeline",    r"\b(how (long|soon)|implementation time|deploy|kitne din|kab tak|deadline)\b"),
    ("competitor",  r"\b(vs\.?|versus|better than|compare|twilio|exotel|knowlarity|servetel)\b"),
]

_OUT_OF_SCOPE_HINTS = {
    "pricing":    "I'm sorry, pricing is highly customised based on your call volume. Would you like to schedule a demo so our product team can walk you through it?",
    "discount":   "I apologize, but discount structures are handled directly by our sales team. Let me know if you’d like to speak with them.",
    "contract":   "Sorry, I don't handle contracts, but our sales team would be happy to discuss the legal details with you on a quick call.",
    "timeline":   "Implementation timelines depend entirely on your setup. I'd recommend a quick demo where our team can give you a realistic estimate.",
    "competitor": "I'd rather not make direct comparisons, sorry! But I'd love to focus on how VoiceFlow can specifically solve your pain points.",
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
