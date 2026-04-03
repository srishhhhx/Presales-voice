"""
test_scope_validation.py -- Unit tests for the scope validator.

Tests keyword blocking, redirect content, and in-scope pass-through.
Run with: pytest tests/test_scope_validation.py -v
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scope_validator import check_scope


# ── Blocked queries ──────────────────────────────────────────────────────────

def test_pricing_query_blocked():
    in_scope, topic, _ = check_scope("how much does it cost?")
    assert not in_scope
    assert topic == "pricing"


def test_discount_query_blocked():
    in_scope, topic, _ = check_scope("can I get a discount?")
    assert not in_scope
    assert topic == "discount"  # discount is its own topic in the scope validator


def test_rate_card_blocked():
    in_scope, topic, _ = check_scope("can you share your rate card?")
    assert not in_scope
    assert topic == "pricing"


def test_contract_query_blocked():
    in_scope, topic, _ = check_scope("what are the contract terms?")
    assert not in_scope
    assert topic == "contract"


def test_competitor_query_blocked():
    in_scope, topic, _ = check_scope("how do you compare with Exotel?")
    assert not in_scope
    assert topic == "competitor"


def test_hindi_pricing_blocked():
    in_scope, topic, _ = check_scope("price kitna hai?")
    assert not in_scope


def test_timeline_query_blocked():
    in_scope, topic, _ = check_scope("how long will implementation take?")
    assert not in_scope


# ── In-scope queries ─────────────────────────────────────────────────────────

def test_use_case_query_allowed():
    in_scope, _, _ = check_scope("we handle 500 calls a day for appointment scheduling")
    assert in_scope


def test_product_capabilities_allowed():
    in_scope, _, _ = check_scope("can your system handle inbound and outbound calls?")
    assert in_scope


def test_demo_request_allowed():
    in_scope, _, _ = check_scope("I would like to schedule a demo")
    assert in_scope


def test_hindi_use_case_allowed():
    in_scope, _, _ = check_scope("हमारी क्लिनिक में रोज़ दो सौ कॉल आती हैं")
    assert in_scope


def test_generic_question_allowed():
    in_scope, _, _ = check_scope("what kind of businesses do you work with?")
    assert in_scope


# ── Redirect hint content ─────────────────────────────────────────────────────

def test_redirect_hint_present_for_out_of_scope():
    in_scope, _, hint = check_scope("what is the price?")
    assert not in_scope
    assert isinstance(hint, str)
    assert len(hint) > 0


def test_no_pricing_in_redirect():
    """Redirect must never contain an actual price or figure."""
    _, _, hint = check_scope("how much does it cost?")
    import re
    # Ensure no currency amounts or specific numbers in the redirect
    assert not re.search(r"₹\d|rs\.\s*\d|\$\d", hint.lower())
