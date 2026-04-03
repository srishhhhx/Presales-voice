# Troubleshooting & Support Guide

This guide covers common errors, edge cases, and architectural constraints you might encounter when running the VoiceFlow AI Presales bot.

## 1. LiveKit Connectivity Issues

**Symptom:** `livekit.agents.rtc.ConnectError: could not connect to room`
* **Cause & Fix:** Your `LIVEKIT_URL` or `LIVEKIT_API_SECRET` is invalid. Ensure your `.env` perfectly matches the credentials in your LiveKit Cloud project settings. Also verify your local internet connection doesn't block WebSocket/WebRTC ports (TCP 443 / UDP 10000-60000).

**Symptom:** The agent connects, but you don't hear anything.
* **Cause & Fix:** Check the LiveKit Agents Playground logs. Ensure your microphone permissions are granted in the browser. Next, verify that `AWS_ACCESS_KEY_ID` has the required `AmazonPollyReadOnlyAccess` permission. If Polly blocks the request, the audio chunks will not generate.

## 2. API Quotas & Timeouts

**Symptom:** `Error: 429 Too Many Requests` in console logs.
* **Cause & Fix:** Groq LPU's free tier has strict Requests Per Minute limits. Ensure you have not exceeded your tokens by running multiple concurrent test bots.

**Symptom:** STT acts sluggish or pauses for 5+ seconds.
* **Cause & Fix:** Deepgram WebSocket timeouts. We have built-in `try/except` suppression arrays that catch broken connections and synthesize a null transcript to keep the bot alive. Check your internet upload speed or consider swapping out your `DEEPGRAM_API_KEY` if the threshold limits trigger.

## 3. Bilingual STT Challenges

**Symptom:** The agent suddenly starts misinterpreting English words as obscure Hindi words.
* **Cause & Fix:** Acoustic crossover. While the `nova-2` `language="hi"` model operates excellently as a Hinglish catcher, strong regional English accents can occasionally trick the acoustic model. If you experience this heavily, you can manually override the speech trigger by explicitly telling Aria: `"Let's switch to English."` This engages `language_detector.py` to securely lock the system out of acoustic misinterpretation.

## 4. VAD (Voice Activity Detection) Fragmentation

**Symptom:** The agent cuts you off mid-sentence and creates a fragmented array in `conversations.jsonl`.
* **Cause & Fix:** Check `src/stt_engine.py`. We have optimized the Deepgram acoustic endpointing (`endpointing_ms=800`) to match Silero VAD (`min_silence_duration=0.8`). If you naturally speak very slowly, increment these numbers to `1200` to give yourself more than a full second of breathing room between sentences.

## 5. Scope Validation Triggers

**Symptom:** The bot refuses to answer a completely innocent query, citing that it belongs to the sales team.
* **Cause & Fix:** False positive in `scope_validator.py`. The regex patterns are heavily enforced. For example, if a user's company is named "Discount Enterprises", the regex target `discount` will mistakenly flag it as an out-of-scope pricing question! Modify the regex tuples in `scope_validator.py` to be more context-aware during staging.
