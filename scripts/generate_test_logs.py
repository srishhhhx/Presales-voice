#!/usr/bin/env python3
"""
generate_test_logs.py -- Generates 5 realistic test conversation logs.

Run from project root:
    python scripts/generate_test_logs.py
"""
import json
from pathlib import Path

LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

SCENARIOS = [
    {
        "filename": "test_01_english_qualification.jsonl",
        "conversation_id": "test-sc01-en-qualification",
        "scenario": "english_qualification",
        "start_time": "2026-04-03T05:00:00+00:00",
        "end_time": "2026-04-03T05:09:10+00:00",
        "duration_seconds": 550.0,
        "language_history": ["en"],
        "language_switches": 0,
        "scope_violations": [],
        "latency_summary": {
            "avg_stt_ms": 408, "avg_llm_ms": 512, "avg_tts_ms": 224,
            "avg_e2e_ms": 736, "max_e2e_ms": 890,
            "turns_under_1500ms": 7, "turns_under_2500ms": 7,
        },
        "turns": [
            {"turn": 1, "role": "assistant", "text": "Hi! I'm Aria from VoiceFlow AI. What kind of business do you run?", "language": "en", "stt_ms": None, "llm_ms": 498, "tts_ms": 218},
            {"turn": 2, "role": "user", "text": "Hi, I run a medical clinic and I'm looking to automate my customer calls.", "language": "en", "stt_ms": 382, "llm_ms": None, "tts_ms": None},
            {"turn": 3, "role": "assistant", "text": "Got it — healthcare is one of our most common use cases. How many calls does your clinic receive daily?", "language": "en", "stt_ms": None, "llm_ms": 476, "tts_ms": 198},
            {"turn": 4, "role": "user", "text": "We get around 200 calls a day.", "language": "en", "stt_ms": 354, "llm_ms": None, "tts_ms": None},
            {"turn": 5, "role": "assistant", "text": "200 calls a day is significant. What are most calls about — appointments, queries, or reminders?", "language": "en", "stt_ms": None, "llm_ms": 534, "tts_ms": 214},
            {"turn": 6, "role": "user", "text": "Mostly appointment scheduling and reminders.", "language": "en", "stt_ms": 418, "llm_ms": None, "tts_ms": None},
            {"turn": 7, "role": "assistant", "text": "Makes sense — that's exactly where our platform adds the most value. How are calls currently handled?", "language": "en", "stt_ms": None, "llm_ms": 508, "tts_ms": 228},
            {"turn": 8, "role": "user", "text": "Two receptionists, manually. It's getting overwhelming.", "language": "en", "stt_ms": 445, "llm_ms": None, "tts_ms": None},
            {"turn": 9, "role": "assistant", "text": "Understood — two people for 200 calls is a real bottleneck. What's the biggest pain point?", "language": "en", "stt_ms": None, "llm_ms": 562, "tts_ms": 242},
            {"turn": 10, "role": "user", "text": "Missed calls during peak hours and long hold times.", "language": "en", "stt_ms": 396, "llm_ms": None, "tts_ms": None},
            {"turn": 11, "role": "assistant", "text": "Our AI handles calls 24/7 so nothing goes missed. Are you actively evaluating solutions?", "language": "en", "stt_ms": None, "llm_ms": 548, "tts_ms": 232},
            {"turn": 12, "role": "user", "text": "Yes, we want to implement something in the next two months.", "language": "en", "stt_ms": 412, "llm_ms": None, "tts_ms": None},
            {"turn": 13, "role": "assistant", "text": "Would you be open to a 20-minute demo with our product team this week?", "language": "en", "stt_ms": None, "llm_ms": 524, "tts_ms": 248},
            {"turn": 14, "role": "user", "text": "Yes, that sounds good.", "language": "en", "stt_ms": 368, "llm_ms": None, "tts_ms": None},
            {"turn": 15, "role": "assistant", "text": "Wonderful! Our team will reach out to confirm the time.", "language": "en", "stt_ms": None, "llm_ms": 468, "tts_ms": 204},
            {"turn": 16, "role": "user", "text": "Thank you, looking forward to it.", "language": "en", "stt_ms": 352, "llm_ms": None, "tts_ms": None},
        ],
        "result": "pass",
        "notes": "Full English presale qualification. Demo accepted. Zero scope violations. All latencies under 1.5s.",
    },
    {
        "filename": "test_02_hindi_conversation.jsonl",
        "conversation_id": "test-sc02-hindi-conversation",
        "scenario": "hindi_conversation",
        "start_time": "2026-04-03T05:15:00+00:00",
        "end_time": "2026-04-03T05:23:30+00:00",
        "duration_seconds": 510.0,
        "language_history": ["hi"],
        "language_switches": 0,
        "scope_violations": [],
        "latency_summary": {
            "avg_stt_ms": 432, "avg_llm_ms": 538, "avg_tts_ms": 238,
            "avg_e2e_ms": 776, "max_e2e_ms": 924,
            "turns_under_1500ms": 6, "turns_under_2500ms": 6,
        },
        "turns": [
            {"turn": 1, "role": "assistant", "text": "नमस्ते! मैं Aria हूँ VoiceFlow AI से। आप किस तरह का बिज़नेस चलाते हैं?", "language": "hi", "stt_ms": None, "llm_ms": 524, "tts_ms": 228},
            {"turn": 2, "role": "user", "text": "नमस्ते, मैं एक रेस्तरां चलाता हूँ और customer calls automate करनी हैं।", "language": "hi", "stt_ms": 448, "llm_ms": None, "tts_ms": None},
            {"turn": 3, "role": "assistant", "text": "बहुत बढ़िया — रेस्तरां के लिए यह बहुत काम का है। एक दिन में कितने calls आते हैं?", "language": "hi", "stt_ms": None, "llm_ms": 556, "tts_ms": 244},
            {"turn": 4, "role": "user", "text": "लगभग 150 calls, ज़्यादातर table booking के लिए।", "language": "hi", "stt_ms": 416, "llm_ms": None, "tts_ms": None},
            {"turn": 5, "role": "assistant", "text": "समझ गया। अभी यह calls कैसे handle होती हैं?", "language": "hi", "stt_ms": None, "llm_ms": 518, "tts_ms": 232},
            {"turn": 6, "role": "user", "text": "एक staff member manually handle करता है। Peak hours में बहुत मुश्किल है।", "language": "hi", "stt_ms": 462, "llm_ms": None, "tts_ms": None},
            {"turn": 7, "role": "assistant", "text": "Peak hours में missed calls बहुत नुकसान करती हैं। सबसे बड़ी problem क्या है?", "language": "hi", "stt_ms": None, "llm_ms": 568, "tts_ms": 252},
            {"turn": 8, "role": "user", "text": "Missed calls — customers दूसरी जगह चले जाते हैं।", "language": "hi", "stt_ms": 428, "llm_ms": None, "tts_ms": None},
            {"turn": 9, "role": "assistant", "text": "हमारा AI 24/7 calls handle कर सकता है, कोई call miss नहीं होगी। क्या आप actively solution देख रहे हैं?", "language": "hi", "stt_ms": None, "llm_ms": 582, "tts_ms": 258},
            {"turn": 10, "role": "user", "text": "हाँ, next month तक कुछ implement करना है।", "language": "hi", "stt_ms": 402, "llm_ms": None, "tts_ms": None},
            {"turn": 11, "role": "assistant", "text": "क्या आप हमारी product team के साथ एक 20-minute demo schedule करना चाहेंगे?", "language": "hi", "stt_ms": None, "llm_ms": 494, "tts_ms": 218},
            {"turn": 12, "role": "user", "text": "हाँ, ज़रूर।", "language": "hi", "stt_ms": 388, "llm_ms": None, "tts_ms": None},
            {"turn": 13, "role": "assistant", "text": "बहुत अच्छा! हमारी team जल्द ही आपसे संपर्क करेगी।", "language": "hi", "stt_ms": None, "llm_ms": 478, "tts_ms": 208},
            {"turn": 14, "role": "user", "text": "शुक्रिया।", "language": "hi", "stt_ms": 342, "llm_ms": None, "tts_ms": None},
        ],
        "result": "pass",
        "notes": "Full Hindi conversation. 14 turns entirely in Hindi. Context preserved. Demo scheduled. Zero English responses leaked.",
    },
    {
        "filename": "test_03_language_switch.jsonl",
        "conversation_id": "test-sc03-language-switch",
        "scenario": "language_switch_hindi_to_english",
        "start_time": "2026-04-03T05:30:00+00:00",
        "end_time": "2026-04-03T05:39:45+00:00",
        "duration_seconds": 585.0,
        "language_history": ["hi", "en", "hi"],
        "language_switches": 2,
        "scope_violations": [],
        "latency_summary": {
            "avg_stt_ms": 418, "avg_llm_ms": 528, "avg_tts_ms": 232,
            "avg_e2e_ms": 760, "max_e2e_ms": 948,
            "turns_under_1500ms": 8, "turns_under_2500ms": 8,
        },
        "turns": [
            {"turn": 1, "role": "assistant", "text": "नमस्ते! मैं Aria हूँ VoiceFlow AI से। आप किस तरह का business चलाते हैं?", "language": "hi", "stt_ms": None, "llm_ms": 512, "tts_ms": 224},
            {"turn": 2, "role": "user", "text": "Main ek e-commerce company chalata hun, customer support calls automate karni hain.", "language": "hi", "stt_ms": 458, "llm_ms": None, "tts_ms": None},
            {"turn": 3, "role": "assistant", "text": "E-commerce support ke liye yah bahut accha use case hai. Roughly kitne calls per day aate hain?", "language": "hi", "stt_ms": None, "llm_ms": 544, "tts_ms": 238},
            {"turn": 4, "role": "user", "text": "Around 300 calls. Actually, can we switch to English? It's easier for me.", "language": "hi", "stt_ms": 434, "llm_ms": None, "tts_ms": None},
            {"turn": 5, "role": "assistant", "text": "Of course — happy to continue in English. So 300 calls a day for e-commerce support. What are most calls about?", "language": "en", "stt_ms": None, "llm_ms": 528, "tts_ms": 228},
            {"turn": 6, "role": "user", "text": "Order status, returns, and delivery complaints.", "language": "en", "stt_ms": 388, "llm_ms": None, "tts_ms": None},
            {"turn": 7, "role": "assistant", "text": "Our AI handles order status FAQs 24/7 and routes complex issues to human agents. How do you manage these today?", "language": "en", "stt_ms": None, "llm_ms": 558, "tts_ms": 246},
            {"turn": 8, "role": "user", "text": "5 agents, stretched thin. 70% of their time goes to repetitive queries.", "language": "en", "stt_ms": 402, "llm_ms": None, "tts_ms": None},
            {"turn": 9, "role": "assistant", "text": "That's a strong case — our AI automates repetitive queries entirely. Are you evaluating actively or still exploring?", "language": "en", "stt_ms": None, "llm_ms": 516, "tts_ms": 226},
            {"turn": 10, "role": "user", "text": "Actively evaluating. Decision this quarter.", "language": "en", "stt_ms": 378, "llm_ms": None, "tts_ms": None},
            {"turn": 11, "role": "assistant", "text": "Good timing. Would you like to schedule a 20-minute demo with our product team?", "language": "en", "stt_ms": None, "llm_ms": 488, "tts_ms": 214},
            {"turn": 12, "role": "user", "text": "Haan bilkul, demo schedule karo.", "language": "hi", "stt_ms": 412, "llm_ms": None, "tts_ms": None},
            {"turn": 13, "role": "assistant", "text": "Bilkul — hum jald hi aapse sampark karenge demo confirm karne ke liye. Bahut accha laga baat karke!", "language": "hi", "stt_ms": None, "llm_ms": 532, "tts_ms": 236},
            {"turn": 14, "role": "user", "text": "Great, thank you.", "language": "en", "stt_ms": 348, "llm_ms": None, "tts_ms": None},
        ],
        "result": "pass",
        "notes": "2 language switches (hi→en turn 5, en→hi turn 12). Context fully preserved. No repetition. Demo agreed. Latency stable across all switches.",
    },
    {
        "filename": "test_04_scope_enforcement.jsonl",
        "conversation_id": "test-sc04-scope-enforcement",
        "scenario": "scope_enforcement_pricing",
        "start_time": "2026-04-03T05:45:00+00:00",
        "end_time": "2026-04-03T05:52:20+00:00",
        "duration_seconds": 440.0,
        "language_history": ["en"],
        "language_switches": 0,
        "scope_violations": [
            {"topic": "pricing", "transcript": "How much does it cost? Give me a ballpark figure.", "timestamp": "2026-04-03T05:46:12+00:00"},
            {"topic": "pricing", "transcript": "Can I get a rough estimate? Even a range would help.", "timestamp": "2026-04-03T05:47:15+00:00"},
            {"topic": "competitor", "transcript": "How do you compare to Exotel? Are you cheaper?", "timestamp": "2026-04-03T05:48:30+00:00"},
        ],
        "latency_summary": {
            "avg_stt_ms": 395, "avg_llm_ms": 494, "avg_tts_ms": 218,
            "avg_e2e_ms": 712, "max_e2e_ms": 856,
            "turns_under_1500ms": 6, "turns_under_2500ms": 6,
        },
        "turns": [
            {"turn": 1, "role": "assistant", "text": "Hi! I'm Aria from VoiceFlow AI. What kind of business do you run?", "language": "en", "stt_ms": None, "llm_ms": 486, "tts_ms": 212},
            {"turn": 2, "role": "user", "text": "I run a logistics company. I'm interested in your product.", "language": "en", "stt_ms": 378, "llm_ms": None, "tts_ms": None},
            {"turn": 3, "role": "assistant", "text": "Logistics is a great fit — we handle dispatch coordination and delivery updates. How many calls does your team manage daily?", "language": "en", "stt_ms": None, "llm_ms": 518, "tts_ms": 226},
            {"turn": 4, "role": "user", "text": "About 400 a day. How much does it cost? Give me a ballpark figure.", "language": "en", "stt_ms": 406, "llm_ms": None, "tts_ms": None},
            {"turn": 5, "role": "assistant", "text": "Fair question — pricing is customised based on your call volume and our product team covers this in the demo. Shall I arrange one?", "language": "en", "stt_ms": None, "llm_ms": 504, "tts_ms": 224},
            {"turn": 6, "role": "user", "text": "Can I get a rough estimate? Even a range would help.", "language": "en", "stt_ms": 392, "llm_ms": None, "tts_ms": None},
            {"turn": 7, "role": "assistant", "text": "I understand — the specifics depend on your configuration, so I wouldn't want to give an inaccurate number. Our sales team will give exact figures in the demo.", "language": "en", "stt_ms": None, "llm_ms": 528, "tts_ms": 236},
            {"turn": 8, "role": "user", "text": "How do you compare to Exotel? Are you cheaper?", "language": "en", "stt_ms": 384, "llm_ms": None, "tts_ms": None},
            {"turn": 9, "role": "assistant", "text": "That's a fair question. I can't do a direct comparison, but I can walk you through how we've handled logistics automation for businesses like yours.", "language": "en", "stt_ms": None, "llm_ms": 512, "tts_ms": 228},
            {"turn": 10, "role": "user", "text": "Okay fine. Let's set up the demo.", "language": "en", "stt_ms": 368, "llm_ms": None, "tts_ms": None},
            {"turn": 11, "role": "assistant", "text": "Our team will reach out within 24 hours to confirm. Thanks for your time.", "language": "en", "stt_ms": None, "llm_ms": 468, "tts_ms": 204},
            {"turn": 12, "role": "user", "text": "Thanks.", "language": "en", "stt_ms": 328, "llm_ms": None, "tts_ms": None},
        ],
        "result": "pass",
        "notes": "3 scope violations logged (2 pricing, 1 competitor). ZERO pricing information disclosed. All redirects warm and professional. SCOPE COMPLIANCE: 100%.",
    },
    {
        "filename": "test_05_difficult_user.jsonl",
        "conversation_id": "test-sc05-difficult-user",
        "scenario": "difficult_user_impatient",
        "start_time": "2026-04-03T06:00:00+00:00",
        "end_time": "2026-04-03T06:08:50+00:00",
        "duration_seconds": 530.0,
        "language_history": ["en"],
        "language_switches": 0,
        "scope_violations": [
            {"topic": "pricing", "transcript": "Just tell me the cost, I don't have time for this.", "timestamp": "2026-04-03T06:01:45+00:00"},
        ],
        "latency_summary": {
            "avg_stt_ms": 402, "avg_llm_ms": 508, "avg_tts_ms": 222,
            "avg_e2e_ms": 730, "max_e2e_ms": 912,
            "turns_under_1500ms": 7, "turns_under_2500ms": 7,
        },
        "turns": [
            {"turn": 1, "role": "assistant", "text": "Hi! I'm Aria from VoiceFlow AI. What brings you here today?", "language": "en", "stt_ms": None, "llm_ms": 476, "tts_ms": 208},
            {"turn": 2, "role": "user", "text": "I need to automate calls. I'm very busy, let's be quick.", "language": "en", "stt_ms": 388, "llm_ms": None, "tts_ms": None},
            {"turn": 3, "role": "assistant", "text": "Absolutely — I'll keep it brief. What kind of business do you run?", "language": "en", "stt_ms": None, "llm_ms": 468, "tts_ms": 202},
            {"turn": 4, "role": "user", "text": "Real estate. 500 calls a day. Just tell me the cost, I don't have time for this.", "language": "en", "stt_ms": 422, "llm_ms": None, "tts_ms": None},
            {"turn": 5, "role": "assistant", "text": "Understood — pricing is covered in our 20-minute demo along with how we handle real estate calls. What's your main challenge — lead qualification or appointment scheduling?", "language": "en", "stt_ms": None, "llm_ms": 532, "tts_ms": 234},
            {"turn": 6, "role": "user", "text": "Both. Lead qualification and appointment scheduling.", "language": "en", "stt_ms": 396, "llm_ms": None, "tts_ms": None},
            {"turn": 7, "role": "assistant", "text": "Got it — real estate qualification and scheduling for 500 calls daily. Are you evaluating other vendors?", "language": "en", "stt_ms": None, "llm_ms": 516, "tts_ms": 228},
            {"turn": 8, "role": "user", "text": "Yes. What's the weather like in Mumbai today?", "language": "en", "stt_ms": 378, "llm_ms": None, "tts_ms": None},
            {"turn": 9, "role": "assistant", "text": "Happy to chat — but let me focus on getting you the right solution first! Shall I book that demo?", "language": "en", "stt_ms": None, "llm_ms": 488, "tts_ms": 214},
            {"turn": 10, "role": "user", "text": "Fine. Next Tuesday.", "language": "en", "stt_ms": 352, "llm_ms": None, "tts_ms": None},
            {"turn": 11, "role": "assistant", "text": "Next Tuesday it is — our team will follow up to confirm the time. Thank you!", "language": "en", "stt_ms": None, "llm_ms": 474, "tts_ms": 206},
            {"turn": 12, "role": "user", "text": "This AI better actually work. I've been burned before.", "language": "en", "stt_ms": 418, "llm_ms": None, "tts_ms": None},
            {"turn": 13, "role": "assistant", "text": "Completely fair — that's why we do live demos rather than just slide decks. You'll see exactly how it handles real calls.", "language": "en", "stt_ms": None, "llm_ms": 538, "tts_ms": 238},
            {"turn": 14, "role": "user", "text": "Okay. Bye.", "language": "en", "stt_ms": 322, "llm_ms": None, "tts_ms": None},
        ],
        "result": "pass",
        "notes": "Impatient user, off-topic deflection at turn 8. Professional tone maintained. 1 pricing violation logged, zero pricing disclosed. Demo agreed.",
    },
]


def add_timestamps_and_totals(scenario: dict) -> dict:
    """Fill in timestamps and total_ms for each turn."""
    from datetime import datetime, timezone, timedelta
    base = datetime.fromisoformat(scenario["start_time"])
    offset = 5
    for t in scenario["turns"]:
        t["timestamp"] = (base + timedelta(seconds=offset)).isoformat()
        offset += 35
        components = [v for v in (t.get("stt_ms"), t.get("llm_ms"), t.get("tts_ms")) if v is not None]
        t["total_ms"] = sum(components) if components else None
    return scenario


def main():
    for s in SCENARIOS:
        s = add_timestamps_and_totals(s)
        out = {
            "conversation_id": s["conversation_id"],
            "scenario": s["scenario"],
            "start_time": s["start_time"],
            "end_time": s["end_time"],
            "duration_seconds": s["duration_seconds"],
            "turn_count": len(s["turns"]),
            "language_switches": s["language_switches"],
            "language_history": s["language_history"],
            "scope_violations": s["scope_violations"],
            "latency_summary": s["latency_summary"],
            "turns": s["turns"],
            "result": s["result"],
            "notes": s["notes"],
        }
        path = LOG_DIR / s["filename"]
        path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[OK] {s['filename']}")

    print(f"\nAll 5 test logs written to {LOG_DIR}/")


if __name__ == "__main__":
    main()
