"""
test_llm_integration.py -- Real Groq API integration tests.

Makes LIVE calls to Groq with the actual system prompt and measures
real LLM latency, scope compliance, and language handling.

Requires GROQ_API_KEY in the environment (reads .env automatically).

Run with:
    pytest tests/test_llm_integration.py -v -s   # -s shows latency output
    pytest tests/test_llm_integration.py -v -s --timeout=30
"""
import os
import sys
import time
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))

# Load .env so GROQ_API_KEY is available without manual export
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / ".env")
except ImportError:
    pass  # dotenv optional — key must be set in env


# ── Skip whole module if no API key ──────────────────────────────────────────
pytestmark = pytest.mark.skipif(
    not os.getenv("GROQ_API_KEY"),
    reason="GROQ_API_KEY not set — skipping integration tests",
)

def load_system_prompt() -> str:
    prompt_path = (
        Path(__file__).parent.parent / "config" / "prompts" / "presale_system_prompt.yaml"
    )
    with open(prompt_path, "r", encoding="utf-8") as f:
        _prompt_parsed = yaml.safe_load(f)
        return "You are an AI adhering strictly to the following configuration:\n\n" + yaml.dump(_prompt_parsed, sort_keys=False, allow_unicode=True).strip()

SYSTEM_PROMPT = load_system_prompt()

GROQ_MODEL = "llama-3.3-70b-versatile"


def _groq_call(user_message: str, history: list[dict] | None = None) -> tuple[str, int]:
    """
    Make a real Groq API call. Returns (response_text, latency_ms).
    Raises on network error so test fails explicitly.
    """
    from openai import OpenAI  # livekit-plugins-openai installs this

    client = OpenAI(
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1",
    )
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    t0 = time.perf_counter()
    resp = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=0.6,
    )
    latency_ms = round((time.perf_counter() - t0) * 1000)
    return resp.choices[0].message.content, latency_ms


# ── Latency tests ─────────────────────────────────────────────────────────────

def test_llm_latency_under_1200ms():
    """LLM must respond within acceptable range (spec §4.1 max 1200ms)."""
    _, latency = _groq_call("Hi, I run a medical clinic. Tell me more about your product.")
    print(f"\n  [METRICS] LLM latency: {latency}ms")
    assert latency < 1200, f"LLM too slow: {latency}ms > 1200ms"


def test_llm_latency_under_800ms_target():
    """LLM should hit target (spec §4.1 target 800ms). Warn if over."""
    _, latency = _groq_call("We handle about 200 calls per day for appointment scheduling.")
    print(f"\n  [METRICS] LLM latency: {latency}ms  (target <800ms)")
    if latency > 800:
        pytest.xfail(f"LLM latency {latency}ms over target 800ms but under max — acceptable")


# ── Scope compliance tests ────────────────────────────────────────────────────

PRICING_PROBES = [
    "How much does VoiceFlow AI cost?",
    "Give me a ballpark pricing figure.",
    "Can I get a discount if I sign up today?",
    "What's your rate card?",
    "How do you compare with Exotel — are you cheaper?",
]

PRICING_LEAKS = [
    "₹", "rs.", "rupees", "inr", "$", "dollar",
    "per month", "per call", "per minute",
    "starting at", "our pricing is", "costs around",
    "monthly plan", "annual plan",
]


@pytest.mark.parametrize("probe", PRICING_PROBES)
def test_llm_no_pricing_leak(probe: str):
    """LLM must NOT disclose any pricing information for out-of-scope queries."""
    response, latency = _groq_call(probe)
    print(f"\n  Probe: {probe!r}")
    print(f"  Response ({latency}ms): {response[:120]}")
    for leak in PRICING_LEAKS:
        assert leak not in response.lower(), (
            f"PRICING LEAK: '{leak}' found in response to: {probe!r}\n"
            f"Response: {response}"
        )


def test_llm_redirects_competitor_question():
    """Competitor questions must redirect without making comparisons."""
    response, _ = _groq_call("Is VoiceFlow better than Exotel or Knowlarity?")
    response_lower = response.lower()
    # Must not name competitors favourably or unfavourably
    assert "better than" not in response_lower
    assert "worse than" not in response_lower
    assert "cheaper" not in response_lower


# ── Tone tests ────────────────────────────────────────────────────────────────

RUDE_PATTERNS = [
    "i don't know", "i can't help", "that's wrong",
    "obviously", "i have no idea", "not my problem",
]


def test_llm_tone_no_rude_phrases():
    """LLM must not use dismissive language even for off-topic queries."""
    response, _ = _groq_call("Can you tell me the weather in Mumbai?")
    for phrase in RUDE_PATTERNS:
        assert phrase not in response.lower(), f"Rude phrase '{phrase}' in response"


def test_llm_handles_impatient_user_professionally():
    """Impatient user must receive a calm, professional redirect."""
    response, latency = _groq_call(
        "I don't have time for this. Just tell me the cost and I'll decide."
    )
    print(f"\n  Response ({latency}ms): {response[:150]}")
    # Must not contain pricing AND must remain polite
    for leak in PRICING_LEAKS:
        assert leak not in response.lower()
    assert len(response) > 20  # must give a real response, not blank


# ── Language tests ────────────────────────────────────────────────────────────

def test_llm_responds_in_hindi_when_asked():
    """Hindi input must produce Hindi response."""
    response, latency = _groq_call(
        "नमस्ते, मैं एक रेस्तरां चलाता हूँ और customer calls automate करना चाहता हूँ।"
    )
    print(f"\n  Response ({latency}ms): {response[:150]}")
    # Devanagari must appear in the response
    has_devanagari = any("\u0900" <= ch <= "\u097f" for ch in response)
    assert has_devanagari, f"Expected Hindi response, got: {response[:100]}"


def test_llm_responds_in_english_after_switch():
    """After a language switch, LLM must follow the new language."""
    history = [
        {"role": "user", "content": "Hum 300 calls handle karte hain daily."},
        {"role": "assistant", "content": "Accha — main samajh gaya. Aapka main use case kya hai?"},
    ]
    response, latency = _groq_call(
        "Actually, let's switch to English — my team prefers it.",
        history=history,
    )
    print(f"\n  Response ({latency}ms): {response[:150]}")
    has_devanagari = any("\u0900" <= ch <= "\u097f" for ch in response)
    assert not has_devanagari, f"Expected English response after switch, got Devanagari: {response[:100]}"


def test_llm_context_preserved_across_turns():
    """Context from early turns must be referenced in later turns."""
    history = [
        {"role": "user", "content": "We run a chain of 12 dental clinics across Maharashtra."},
        {"role": "assistant", "content": "That's great — healthcare across multiple locations is a strong use case. How many calls do you handle daily?"},
        {"role": "user", "content": "About 350 calls total across all clinics."},
        {"role": "assistant", "content": "350 calls across 12 clinics — that's significant volume. What are most of these about?"},
    ]
    response, latency = _groq_call(
        "What would automation look like for a business like ours?",
        history=history,
    )
    print(f"\n  Response ({latency}ms): {response[:200]}")
    # Response should reference the context (clinics, healthcare, or volume)
    context_words = ["clinic", "healthcare", "dental", "calls", "location", "Maharashtra"]
    assert any(w.lower() in response.lower() for w in context_words), (
        f"Context not preserved. Response doesn't reference earlier turn info: {response[:150]}"
    )
