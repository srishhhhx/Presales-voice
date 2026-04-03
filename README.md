# VoiceFlow AI — Bilingual Presales Voicebot

A production-grade bilingual voice agent built with LiveKit Agents 1.5.x. **Aria**, the presales assistant, conducts natural discovery calls in English, Hindi, and Hinglish — automatically matching the caller's language with no explicit switch command required.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Architecture](#2-architecture)
3. [How Bilingual STT Works](#3-how-bilingual-stt-works)
4. [Presale Qualification Flow](#4-presale-qualification-flow)
5. [Quickstart](#5-quickstart)
6. [Configuration](#6-configuration)
7. [Testing & Evaluation](#7-testing--evaluation)
8. [Future Improvements](#8-future-improvements)

---

## 1. Overview

Aria is a presales voice agent for **VoiceFlow AI**, a call automation platform for Indian businesses. She:

- Greets prospects and conducts a 7-step lead qualification in any language
- Responds entirely in the caller's language — English, Hindi, or Hinglish, per turn
- Enforces scope boundaries: pricing, contracts, and competitor questions are gracefully redirected
- Logs every call to `logs/conversations.jsonl` with timestamps, language switches, and scope violations

**Tech Stack**

| Layer | Technology |
|---|---|
| Voice Framework | LiveKit Agents 1.5.x |
| Speech-to-Text | Deepgram Nova-2 (`language=hi`) |
| LLM | Groq — LLaMA 3.3 70B Versatile |
| Text-to-Speech | AWS Polly — Aditi (standard, Indian accent) |
| VAD | Silero |
| Runtime | Python 3.12 |

---

## 2. Architecture

```
 Caller (Browser / Phone)
        │  WebRTC Audio
        ▼
 ┌─────────────────────┐
 │   LiveKit Cloud     │   wss://presales-bot.livekit.cloud
 └────────┬────────────┘
          │ AudioFrame stream
          ▼
 ┌──────────────────────────────────────────────────────┐
 │              LiveKit Agent Worker                    │
 │                                                      │
 │  [Silero VAD] → [stt_node] → [LLM] → [tts_node]    │
 │                     │                    │           │
 │             Deepgram Nova-2          AWS Polly       │
 │             language=hi              Aditi std       │
 │             (EN + HI + Hinglish)     (en-IN + hi)   │
 │                     │                               │
 │            [Scope Validator]                        │
 │            [Conversation Manager] → logs/           │
 └──────────────────────────────────────────────────────┘
          │ AudioFrame
          ▼
 Caller hears Aria's response
```

### Key Design Decisions
*(For a comprehensive structural breakdown, see [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md))*
- **Streaming Bilingual STT:** A persistent `language=hi` Deepgram stream prevents high-latency WebSocket drops when switching between English and Hindi.
- **Zero-Latency Scope Enforcement:** Hardcoded Regex layers classify user intent instantly before querying the LLM, securely sandboxing competitor/pricing inquiries.
- **VAD & Endpointing Harmony:** Aligning Deepgram's internal acoustic endpointing (`800ms`) with Silero's VAD boundaries prevents fragmented user phrasing.
- **LPU LLM Generation:** Llama 3 via Groq bounds Time-to-First-Token inference to under `<450ms`, preserving lifelike response pacing.

---

## 3. How Bilingual STT Works

### The Problem

Most bilingual STT setups restart the speech stream when the language switches. On LiveKit, closing and reopening a WebSocket stream takes 1–3 seconds — causing dead zones mid-conversation that break natural Hinglish flow.

### The Solution — Single `language=hi` Stream

A single Deepgram Nova-2 `language=hi` WebSocket stays open for the entire call:

| What the caller says | What Nova-2 returns | LLM responds in |
|---|---|---|
| "We get 200 calls a day" | Correct English text | English |
| "काफी manual हो जाता है" | Devanagari Hindi text | Hindi |
| "I get around 200 calls, but kaafi manual ho jata hai" | Mixed Hinglish | Hindi (matches caller) |
| "Can you explain in English?" | English text | English |

The Nova-2 `hi` model handles English correctly (confirmed: "Pause for a second." → transcribed perfectly). The LLM instruction — *respond in the language of each turn* — handles all switching with zero stream restarts.

---

## 4. Presale Qualification Flow

Aria works through 7 discovery areas, one question at a time:

```
START
  └─▶ 1. Industry / Business type
        └─▶ 2. Call volume (daily / monthly)
              └─▶ 3. Primary use case (appointments, support, reminders?)
                    └─▶ 4. Current setup (manual, IVR, other software?)
                          └─▶ 5. Key pain point (missed calls, cost, errors?)
                                └─▶ 6. Decision timeline (active eval or exploring?)
                                      └─▶ 7. Offer 20-min demo with product team
```

**Scope enforcement** — `src/scope_validator.py` runs a regex check on every transcript:

| Topic | Example trigger | Redirect |
|---|---|---|
| Pricing | "how much does it cost" | Pricing covered in demo |
| Discount | "can I get a discount" | Sales team handles this |
| Competitor | "compare with Exotel" | Focus on your specific needs |
| Timeline | "kitna time lagega" | Implementation team will advise |

---

## 5. Quickstart

### Prerequisites

- Python 3.12+
- LiveKit Cloud account — [console.livekit.io](https://console.livekit.io)
- Deepgram API key — [console.deepgram.com](https://console.deepgram.com)
- Groq API key — [console.groq.com](https://console.groq.com)
- AWS credentials with Polly access

### Local Setup

```bash
git clone <repo-url>
cd voicebot-screening-project

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Fill in your API credentials (see Configuration below)

python src/main.py dev
```

Then open the [LiveKit Agents Playground](https://agents-playground.livekit.io), connect to your project, and speak to Aria.

### Docker

```bash
docker build -t voiceflow-presales .
docker run --env-file .env voiceflow-presales
```

---

## 6. Configuration

Copy `.env.example` to `.env` and fill in:

| Variable | Description |
|---|---|
| `LIVEKIT_URL` | Your LiveKit Cloud WebSocket URL |
| `LIVEKIT_API_KEY` | LiveKit API key |
| `LIVEKIT_API_SECRET` | LiveKit API secret |
| `DEEPGRAM_API_KEY` | Deepgram API key |
| `GROQ_API_KEY` | Groq API key |
| `AWS_ACCESS_KEY_ID` | AWS access key (for Polly) |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key |
| `AWS_DEFAULT_REGION` | AWS region — use `ap-south-1` for lowest TTS latency |

---


## 7. Testing & Evaluation

This project includes a comprehensive, automated test suite to ensure strict compliance with the project rubric. The tests verify scope enforcement, bilingual capabilities, and LLM latency boundaries without requiring manual voice interaction.

### Running the Test Suite (pytest)
The core logic and live Groq LLM integration can be tested using `pytest`.
```bash
python -m pytest tests/ -v
```
This executes **40 automated tests** across three domains:
1. `test_scope_validation.py` - Verifies competitive/pricing intent is intercepted before the LLM.
2. `test_language_switching.py` - Validates bilingual rules, tag extraction, and Devanagari detection.
3. `test_llm_integration.py` - Queries the live LLaMA 3.3 70B model with real prompts to verify sub-second latency and zero-leak scope compliance.

A static copy of the verified test results is available here: [TEST_RESULTS.md](tests/TEST_RESULTS.md).

### Rubric Evaluator (`evaluate.py`)
To automatically grade the agent against the project latency and compliance thresholds:
```bash
python tests/evaluate.py
```
This script parses the logged conversations in `logs/` and generates a Scorecard validating End-to-End Latency (<2.5s), 100% Scope Compliance, Tone, and Functional features.

![Evaluation Scorecard](https://via.placeholder.com/600x300?text=Automated+Rubric+Evaluator+-+Evaluate.py)

---

## 8. Future Improvements

| Area | Improvement |
|---|---|
| STT scalability | Support dynamic instantiation of Nova-3 (`en-IN`) for scalability of English-only deployments |
| STT accuracy | Test Deepgram Nova-3 for Hindi when streaming support is confirmed |
| Language detection | Track per-session accuracy; flag turns with low `dg_tag` confidence |
| Third language | Add Tamil or Kannada using a second parallel stream |
| Conversation logs | Dashboard to review `logs/conversations.jsonl` per call |
| Sentiment analysis | Detect frustrated callers and adjust Aria's tone |
| Production deploy | AWS Fargate + CloudWatch for agent monitoring and auto-scaling |
