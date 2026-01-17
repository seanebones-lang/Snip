# X.AI TTS Implementation - Complete

## Overview
Successfully replaced the external TTS API (which was down) with X.AI's Grok Voice Agent API for text-to-speech generation.

## Implementation Details

### Backend Changes (`backend/app/main.py`)

1. **Added X.AI TTS Helper Functions:**
   - `get_xai_ephemeral_token()`: Gets short-lived token for WebSocket connection
   - `generate_xai_tts_audio()`: Generates TTS audio via WebSocket using X.AI Grok Voice Agent API
   - `convert_pcm_to_wav()`: Converts PCM audio to WAV format for browser compatibility

2. **Updated Chat Endpoint:**
   - Replaced external TTS API call with X.AI TTS integration
   - Only generates TTS when provider is 'xai' (X.AI)
   - Returns base64-encoded WAV audio as data URL

3. **Dependencies Added:**
   - `websockets==12.0` (for WebSocket connections)
   - `httpx` (already present, used for async HTTP requests)

### How It Works

1. **Ephemeral Token**: Gets a short-lived token from X.AI API
2. **WebSocket Connection**: Connects to `wss://api.x.ai/v1/realtime`
3. **Session Configuration**: Configures voice (Ara, Leo, Rex, Sal, or Eve) and audio format
4. **Text Input**: Sends text via `user.text` message
5. **Audio Reception**: Listens for `assistant.audio` messages and collects audio chunks
6. **Format Conversion**: Converts PCM audio to WAV format
7. **Base64 Encoding**: Encodes WAV as base64 data URL for browser playback

### Supported Voices

- **Ara** (Female, Warm, Friendly) - Default
- **Rex** (Male, Confident, Clear)
- **Sal** (Neutral, Smooth, Balanced)
- **Eve** (Female, Energetic, Upbeat)
- **Leo** (Male, Authoritative, Strong)

### Audio Format

- **Input Format**: PCM (Linear16) at 24kHz
- **Output Format**: WAV (converted from PCM) at 24kHz, 16-bit, mono
- **Delivery**: Base64-encoded data URL (`data:audio/wav;base64,...`)

## Testing

### Test Script
A test script is available at `backend/test_xai_tts.py`:

```bash
cd backend
export XAI_API_KEY="your-api-key-here"
python -m backend.test_xai_tts
```

This will:
1. Generate TTS audio for a test phrase
2. Convert PCM to WAV
3. Save to `test_output.wav` for verification

### End-to-End Testing

1. **Start the backend server**
2. **Send a chat request** via POST to `/api/chat` with:
   - `client_id`: Valid client UUID
   - `message`: Test message
   - Provider must be 'xai' with valid X.AI API key

3. **Check response**:
   - Should include `audio_url` field with base64 data URL
   - Widget should automatically play the audio

### Widget Integration

The widget (`widget/src/widget.ts`) already supports:
- ✅ Receiving `audio_url` from backend response
- ✅ Playing base64 data URLs via `Audio` API
- ✅ Fallback to browser TTS if backend audio fails

No widget changes needed - it will automatically use the X.AI-generated audio when available.

## Error Handling

- **Non-fatal**: TTS failures don't break chat functionality
- **Graceful degradation**: If TTS fails, chat still works (just no audio)
- **Logging**: All TTS operations are logged with `[X.AI TTS]` prefix
- **Timeout**: 30-second timeout for audio generation
- **Retry**: Not implemented (could be added if needed)

## Configuration

### Required Environment Variables

- `XAI_API_KEY`: Your X.AI API key (for global fallback)
- Or set per-client via dashboard: `ai_api_key` in client config

### Client Configuration

Clients can configure:
- `ai_provider`: Must be 'xai' for TTS to work
- `ai_api_key`: Client's own X.AI API key (optional, falls back to global)
- `ai_model`: Model to use (default: 'grok-3-fast')

## Performance Considerations

- **Latency**: WebSocket connection adds ~1-2 seconds overhead
- **Audio Size**: Typical response generates 50-200KB of audio
- **Base64 Overhead**: ~33% size increase for base64 encoding
- **Timeout**: 30 seconds max for audio generation

## Known Limitations

1. **WebSocket Overhead**: Each TTS request requires a new WebSocket connection
2. **No Caching**: Audio is generated fresh for each response
3. **Single Voice**: Currently uses "Ara" voice (can be made configurable)
4. **No Streaming**: Waits for complete audio before returning

## Future Improvements

- [ ] Cache ephemeral tokens (they're short-lived but could be reused briefly)
- [ ] Make voice configurable per client
- [ ] Add audio caching for repeated responses
- [ ] Support streaming audio delivery
- [ ] Add retry logic for failed TTS requests

## Troubleshooting

### No Audio Generated

1. Check API key is valid: `XAI_API_KEY` or client's `ai_api_key`
2. Check provider is 'xai': Verify `ai_provider` in client config
3. Check logs for `[X.AI TTS]` messages
4. Verify WebSocket connection isn't blocked by firewall

### Audio Playback Issues

1. Check browser console for audio playback errors
2. Verify base64 data URL format is correct
3. Test with `test_xai_tts.py` to verify audio generation works
4. Check browser supports WAV format (all modern browsers do)

### Timeout Errors

1. Increase timeout in `generate_xai_tts_audio()` if needed
2. Check network connectivity to `api.x.ai`
3. Verify X.AI API is operational

## References

- X.AI Grok Voice Agent API Documentation: https://docs.x.ai/docs/guides/voice
- WebSocket Endpoint: `wss://api.x.ai/v1/realtime`
- Ephemeral Token Endpoint: `https://api.x.ai/v1/realtime/client_secrets`
