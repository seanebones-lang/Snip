# Grok Voice Agent API (xAI)

Reference for the xAI Grok Voice Agent API. Snip uses this API for **text-to-speech** (TTS) over the same WebSocket endpoint.

---

## Overview

**Grok Voice Agent API** – Build real-time voice applications with Grok via WebSocket (voice assistants, phone agents, IVR).

- **WebSocket endpoint:** `wss://api.x.ai/v1/realtime`
- **Region:** us-east-1 only
- **Ephemeral token:** `https://api.x.ai/v1/realtime/client_secrets`

Dedicated speech-to-text and text-to-speech APIs are coming later.

---

## Capabilities

| Feature | Description |
|--------|-------------|
| **Real-time voice** | Full duplex voice over WebSocket |
| **Tool calling** | Web Search, X Search, Collections (RAG), custom functions |
| **Multilingual** | 100+ languages, natural accents, auto language detection |
| **Low latency** | Optimized for real-time conversation |
| **Audio formats** | PCM (8–48 kHz), G.711 μ-law, G.711 A-law |

---

## Voices

| Voice | Type | Tone | Description |
|-------|------|------|-------------|
| **Ara** | Female | Warm, friendly | Default, conversational |
| **Rex** | Male | Confident, clear | Business / professional |
| **Sal** | Neutral | Smooth, balanced | General purpose |
| **Eve** | Female | Energetic, upbeat | Interactive / engaging |
| **Leo** | Male | Authoritative, strong | Instructional |

---

## Use Cases

- Voice assistants (web and mobile)
- AI phone systems (e.g. Twilio)
- Real-time customer support
- IVR systems

---

## Example Architectures (from xAI)

- **Web:** Browser (React) ↔ WebSocket ↔ Backend (FastAPI/Express) ↔ WebSocket ↔ xAI API  
- **Phone:** Phone ↔ SIP ↔ Twilio ↔ WebSocket ↔ Node ↔ xAI API  
- **WebRTC:** Browser ↔ WebRTC ↔ Backend ↔ WebSocket ↔ xAI API  

Third-party: LiveKit, Voximplant, Pipecat (native Grok Voice Agent integration).

---

## Relation to Snip

Snip uses the **same** Grok Voice Agent API endpoint for **TTS only**:

1. **Chat flow:** User types in widget → backend calls xAI Chat Completions for text → backend calls `wss://api.x.ai/v1/realtime` with that text → receives PCM audio → converts to WAV and returns `audio_url` (base64) to the widget.
2. **TTS trick:** The Voice Agent is conversational (user says X → assistant says Y). We send our bot's reply text as the "user" message and set session instructions so the agent **speaks that text verbatim** instead of replying to it. See `backend/app/main.py` – `generate_tts_audio()` session instructions.
3. **Implementation:** `backend/app/main.py` – `generate_tts_audio()`, `get_ephemeral_token()`, `convert_pcm_to_wav()`; see `XAI_TTS_IMPLEMENTATION.md`.
4. **Future:** To support **real-time voice** (user speaks, Grok responds with voice over WebSocket), Snip would need a WebSocket path from widget ↔ backend ↔ `wss://api.x.ai/v1/realtime` with bidirectional audio (e.g. browser mic → backend → xAI, xAI audio → backend → widget). That would be a separate mode from the current “type + play TTS” flow.

---

*Source: xAI Grok Voice Agent API documentation (us-east-1).*
