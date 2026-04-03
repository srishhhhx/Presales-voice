# System Architecture

The VoiceFlow AI Presales bot is composed of modular elements working together in strict orchestration via WebRTC and LiveKit Agents. This document outlines the rationale, component breakdown, and specific pipeline optimizations achieved in this codebase.

## 1. High-Level Pipeline

The system is deployed using a standard Audio-In/Audio-Out streaming pipeline over WebRTC. The orchestration is handled entirely within `src/main.py` via an `AgentSession`.

**Flow:**
`User Audio -> LiveKit Room -> Silero VAD -> Deepgram STT -> Scope Validator -> Llama 3 LLM -> AWS Polly TTS -> LiveKit Room -> User`

---

## 2. Component Decisions & Rationale

### 2.1 Voice Activity Detection (VAD)
**Tool:** Silero VAD (Local computation)
**Decision Scope:** We needed a way to control turn-taking locally without incurring API round-trips.
**Settings:** We implemented a `min_speech_duration` of `0.01s` (rapid acoustic pickup) and a completely decoupled `min_silence_duration` of `0.8s`. This 0.8s buffer allows human users to comfortably pause mid-sentence to think or draw a breath without the bot rudely barging in and splitting their turn.

### 2.2 Speech-to-Text (STT) + Language Detection
**Tool:** Deepgram Nova-2 (`language=hi`)
**Decision Scope:** Handling true Hinglish seamlessly without WebRTC stream dropout penalties.
**Implementation details:**
Unlike standard implementations that constantly tear down and recreate WebSocket streams when a user switches from English to Hindi (which usually introduces a 2-second crash-pause mid-conversation), we configured our pipeline to **persistently stream through Deepgram's Hindi model (`language=hi`)**. 
The `nova-2` `hi` acoustic model was designed natively for India and correctly parses both deep English syntax and raw Devanagari Hindi via pure acoustic alignment. This gives the bot zero-latency Hinglish and language switching capabilities without ever needing to restart the TCP socket.
*Note: We also strictly forced `endpointing_ms=800` into the Deepgram payload to stop its internal micro-pause engine from overriding our Silero VAD config.*

### 2.3 LLM Processing Engine
**Tool:** Groq LPU + Meta Llama 3.3 70B Versatile
**Decision Scope:** The absolute lowest TTFT (Time To First Token) currently possible. 
**Implementation details:**
Because presales pipelines require the bot to respond almost instantly to maintain engagement, we migrated away from OpenAI standard APIs (which can have 1.2s+ latency bounds) and utilized Groq's dedicated LPUs. This drops LLM response generation to roughly `~450ms`. All system behaviors, including the complex 7-step qualification pipeline, are structurally enforced via a highly cacheable YAML configuration file (`config/prompts/presale_system_prompt.yaml`).

### 2.4 Safety, Scope & Tone Overriding
**Tool:** Python Regex (`src/scope_validator.py`) + VADER (`vaderSentiment`)
**Decision Scope:** Security against adversarial prompt injections and bad UI behaviors.
**Implementation details:**
Rather than relying completely on the LLM to understand when it is violating boundary rules, we built a zero-latency upstream text classifier. 
1. **Scope:** Before a text token ever enters the LLM context array, `scope_validator.py` applies hard regex matching against pricing, competitor, and discount parameters. If flagged, the LLM is forcibly instructed to pivot away.
2. **Tone:** We run a `vaderSentiment` matrix over the incoming user text chunk natively in memory (takes <2ms). If the user is flagged as angry or highly upset, we prepend an ephemeral `[SYSTEM NOTE]` into the LLM context to drastically alter the bot's tone to be hyper-empathetic.

### 2.5 Text-to-Speech (TTS)
**Tool:** AWS Polly (Aditi - Standard Engine)
**Decision Scope:** Realism combined with speed.
**Implementation details:**
The `Aditi` voice matrix is deployed via Amazon's standard engine (which generates bytes 3x faster than their Neural or Generative models, pushing TTS stream latency comfortably into the `~250ms` zone). In addition, `Aditi` acts as a natively pronounced Indian-English anchor natively capable of generating both English phrasing and Hindi phrases (including Devanagari script output from the LLM) without mispronouncing local vernacular. Before audio generation, we run a strict regex filter over the LLM output `re.sub(r'[^\u0900-\u097Fa-zA-Z0-9\s.,!?"\'-]')` to prevent hallucinated foreign script (like Vietnamese or Chinese) from crashing the TTS engine.

### 2.6 Analytics & Logging Mechanism
**Tool:** Built-in Python Threading (`ConversationManager`)
**Decision Scope:** Persisting stateless LiveKit objects into long-lived memory for evaluation.
**Implementation details:**
Because LiveKit agent pods immediately self-destruct upon call termination, data capture is critical. We capture `stt_node` and `tts_node` text payloads synchronously. To assess latency without API guessing, `main.py` explicitly captures `time.monotonic()` when the final text chunk arrives and diffs it immediately when the very first byte of AWS TTS audio is flushed to the WebRTC queue. When the caller hangs up, `session.on_disconnected` guarantees that the final JSONL array is safely dumped into `/logs/conversations.jsonl`.
