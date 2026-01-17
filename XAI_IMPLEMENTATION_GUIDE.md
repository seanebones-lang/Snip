# X.AI Chatbot Implementation Guide

## Overview

This guide provides practical implementation steps for integrating X.AI models into your chatbots, including API configuration, voice integration, and code snippets. Based on X.AI Enterprise API documentation (current as of January 2026).

---

## 1. Setting Your Chatbots to the Right API and Model

### Step 1: Obtain and Validate API Key

**Get API Key Information**:
```python
import requests
import os

API_KEY = os.getenv('XAI_API_KEY')
BASE_URL = 'https://api.x.ai/v1'

def get_api_key_info():
    """Get information about your API key"""
    headers = {'Authorization': f'Bearer {API_KEY}'}
    response = requests.get(f'{BASE_URL}/api-key', headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"Key Status: {'Active' if not data.get('api_key_disabled') else 'Disabled'}")
        print(f"ACLs: {data.get('acls', [])}")
        return data
    return None
```

**Check Permissions**:
- Ensure `api-key:endpoint:*` or `api-key:endpoint:chat` in ACLs
- Ensure `api-key:model:*` or specific model in ACLs
- Verify key is not blocked or disabled

### Step 2: List Available Models

**Get Model Information**:
```python
def get_models():
    """Get detailed model information with pricing and features"""
    headers = {'Authorization': f'Bearer {API_KEY}'}
    
    # Get language models (detailed)
    response = requests.get(f'{BASE_URL}/language-models', headers=headers)
    if response.status_code == 200:
        return response.json()['models']
    return None

def get_model_info(model_id):
    """Get specific model information"""
    headers = {'Authorization': f'Bearer {API_KEY}'}
    response = requests.get(f'{BASE_URL}/language-models/{model_id}', headers=headers)
    if response.status_code == 200:
        return response.json()
    return None
```

**Recommended Models** (as of January 2026):

| Use Case | Recommended Model | Pricing (per million tokens) | Context |
|----------|------------------|------------------------------|---------|
| **Agentic Tool Calling** | `grok-4-1-fast-non-reasoning` | $0.20/$0.50 | 2M |
| **General Chat** | `grok-4-fast-non-reasoning` | $0.20/$0.50 | 2M |
| **Cost-Effective** | `grok-3-mini` | $0.30/$0.50 | 131K |
| **Coding Tasks** | `grok-code-fast-1` | $0.20/$1.50 | 256K |
| **Image Understanding** | `grok-2-vision-1212` | $2.00/$10.00 | 32K |
| **Image Generation** | `grok-2-image-1212` | $0.07/image | N/A |

**⚠️ Important**: 
- `grok-4-0709` is more expensive ($3.00/$15.00) - use fast models instead
- Chat Completions (`/v1/chat/completions`) is **deprecated**
- **Recommended**: Use Responses API (`/v1/responses`)

### Step 3: Configure Chatbot to Use API

#### Option A: Responses API (Recommended)

```python
def chat_completion_responses_api(messages, model='grok-4-1-fast-non-reasoning'):
    """
    Use Responses API (recommended) - replaces deprecated Chat Completions
    """
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Convert messages format for Responses API
    input_messages = []
    for msg in messages:
        input_messages.append({
            'role': msg['role'],
            'content': msg['content']
        })
    
    data = {
        'input': input_messages,
        'model': model,
        'store': True  # Store for 30 days, enables continuation
    }
    
    response = requests.post(f'{BASE_URL}/responses', headers=headers, json=data)
    
    if response.status_code == 200:
        result = response.json()
        # Extract text from output
        if result.get('output') and len(result['output']) > 0:
            output_item = result['output'][0]
            if output_item.get('content') and len(output_item['content']) > 0:
                text_content = output_item['content'][0].get('text', '')
                return {
                    'text': text_content,
                    'response_id': result.get('id'),  # Use for continuation
                    'usage': result.get('usage', {})
                }
    
    raise Exception(f'Error: {response.status_code} - {response.text}')
```

#### Option B: Chat Completions (Legacy - Deprecated)

```python
def chat_completion_legacy(messages, model='grok-4-1-fast-non-reasoning'):
    """
    Legacy Chat Completions endpoint (deprecated - use Responses API instead)
    """
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'messages': messages,
        'model': model
    }
    
    response = requests.post(f'{BASE_URL}/chat/completions', headers=headers, json=data)
    
    if response.status_code == 200:
        result = response.json()
        return {
            'text': result['choices'][0]['message']['content'],
            'usage': result.get('usage', {}),
            'system_fingerprint': result.get('system_fingerprint')
        }
    
    raise Exception(f'Error: {response.status_code} - {response.text}')
```

### Step 4: Best Practices

**Tokenization**:
```python
def tokenize_text(text, model='grok-4-1-fast-non-reasoning'):
    """Tokenize text to manage costs and limits"""
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    
    data = {'text': text, 'model': model}
    response = requests.post(f'{BASE_URL}/tokenize-text', headers=headers, json=data)
    
    if response.status_code == 200:
        tokens = response.json().get('token_ids', [])
        return len(tokens)
    return None
```

**Error Handling**:
```python
def safe_chat_completion(messages, model='grok-4-1-fast-non-reasoning'):
    """Chat completion with error handling"""
    try:
        result = chat_completion_responses_api(messages, model)
        
        # Log usage for monitoring
        usage = result.get('usage', {})
        print(f"Tokens used: {usage.get('total_tokens', 0)}")
        print(f"Prompt: {usage.get('prompt_tokens', 0)}")
        print(f"Completion: {usage.get('completion_tokens', 0)}")
        
        return result['text']
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            print("Bad request - check message format")
        elif e.response.status_code == 422:
            print("Validation error - check parameters")
        elif e.response.status_code == 404:
            print("Model or endpoint not found")
        elif e.response.status_code == 401:
            print("Invalid API key")
        else:
            print(f"HTTP Error: {e.response.status_code}")
        raise
    except Exception as e:
        print(f"Error: {e}")
        raise
```

**Deferred Completions** (for long-running queries):
```python
import time

def deferred_completion(messages, model='grok-4-1-fast-non-reasoning', timeout=600):
    """Create deferred completion and poll for result"""
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Create deferred request (set deferred flag)
    data = {
        'messages': messages,
        'model': model,
        'deferred': True  # Request deferred completion
    }
    
    response = requests.post(f'{BASE_URL}/chat/completions', headers=headers, json=data)
    
    if response.status_code == 200:
        request_data = response.json()
        request_id = request_data.get('request_id')
        
        # Poll for result
        start_time = time.time()
        while time.time() - start_time < timeout:
            result_response = requests.get(
                f'{BASE_URL}/chat/deferred-completion/{request_id}',
                headers={'Authorization': f'Bearer {API_KEY}'}
            )
            
            if result_response.status_code == 200:
                result = result_response.json()
                return result['choices'][0]['message']['content']
            elif result_response.status_code == 202:
                # Still processing
                time.sleep(5)  # Poll every 5 seconds
            else:
                raise Exception(f"Error: {result_response.status_code}")
        
        raise TimeoutError("Deferred completion timeout")
    
    raise Exception(f'Error: {response.status_code} - {response.text}')
```

---

## 2. Integrating Voice Response

### Important Update: X.AI Has Native TTS Support!

**X.AI now provides native TTS via Grok Voice Agent API** - no need for third-party TTS services! We've implemented this in the backend.

### Option 1: X.AI Native TTS (Recommended - Already Implemented)

**Backend Implementation** (already done):
- Uses Grok Voice Agent API via WebSocket
- Connects to `wss://api.x.ai/v1/realtime`
- Generates audio in PCM format, converts to WAV
- Returns base64-encoded audio data URL
- Supports 5 voices: Ara, Leo, Rex, Sal, Eve

**How It Works**:
1. Backend generates text response via X.AI API
2. Backend calls `generate_xai_tts_audio()` function
3. Gets ephemeral token for WebSocket connection
4. Connects to Voice Agent API and generates audio
5. Converts PCM to WAV and base64-encodes
6. Returns `audio_url` in response (e.g., `data:audio/wav;base64,...`)
7. Widget automatically plays audio

**Usage** (automatic):
- When provider is 'xai', TTS is automatically generated
- Widget receives `audio_url` in chat response
- Browser plays audio automatically
- Falls back to browser TTS if X.AI TTS fails

### Option 2: Hybrid Approach (For Non-X.AI Providers)

**For providers without native TTS** (OpenAI, Anthropic), use client-side TTS:

**JavaScript Example**:
```javascript
// Voice Input (STT) - Client-side
function startVoiceInput() {
  if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
    alert('Speech recognition not supported');
    return;
  }
  
  const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
  recognition.continuous = false;
  recognition.interimResults = false;
  
  recognition.onresult = async (event) => {
    const transcript = event.results[0][0].transcript;
    console.log('User said:', transcript);
    
    // Send to backend
    const response = await sendToBackend(transcript);
    
    // Play response as voice
    speakResponse(response);
  };
  
  recognition.onerror = (event) => {
    console.error('Speech recognition error:', event.error);
  };
  
  recognition.start();
}

// Voice Output (TTS) - Client-side fallback
function speakResponse(text) {
  if ('speechSynthesis' in window) {
    // Cancel any ongoing speech
    window.speechSynthesis.cancel();
    
    const utterance = new SpeechSynthesisUtterance(text);
    
    // Try to find a British English voice
    const voices = window.speechSynthesis.getVoices();
    const britishVoice = voices.find(v => 
      v.lang.includes('en-GB') || 
      v.name.toLowerCase().includes('british') ||
      v.name.toLowerCase().includes('uk')
    );
    
    if (britishVoice) {
      utterance.voice = britishVoice;
    }
    
    utterance.rate = 0.95;
    utterance.pitch = 1.0;
    utterance.volume = 1.0;
    
    utterance.onerror = (e) => {
      console.error('Speech synthesis error:', e);
    };
    
    window.speechSynthesis.speak(utterance);
  }
}

// Send to backend and get response
async function sendToBackend(userInput) {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      client_id: CLIENT_ID,
      message: userInput
    })
  });
  
  const data = await response.json();
  
  // If backend provides audio_url (X.AI TTS), use it
  if (data.audio_url) {
    const audio = new Audio(data.audio_url);
    audio.play().catch(err => {
      console.error('Audio playback error:', err);
      // Fallback to browser TTS
      speakResponse(data.response);
    });
  } else {
    // Fallback to browser TTS
    speakResponse(data.response);
  }
  
  return data.response;
}
```

**Python Example (Server-side STT/TTS)**:
```python
# Note: This is for reference - actual implementation uses X.AI TTS
import speech_recognition as sr
import pyttsx3

def voice_input():
    """Convert voice to text using speech recognition"""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)
    
    try:
        text = r.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return None
    except sr.RequestError as e:
        print(f"STT error: {e}")
        return None

def voice_output(text):
    """Convert text to speech using pyttsx3"""
    engine = pyttsx3.init()
    
    # Set voice properties
    voices = engine.getProperty('voices')
    # Try to find British English voice
    for voice in voices:
        if 'british' in voice.name.lower() or 'uk' in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break
    
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 1.0)
    
    engine.say(text)
    engine.runAndWait()
```

### Current Implementation Status

**✅ X.AI TTS**: Already implemented in backend
- Location: `backend/app/main.py`
- Function: `generate_xai_tts_audio()`
- Automatic: Works when provider is 'xai'
- Output: Base64-encoded WAV audio data URL

**✅ Widget Support**: Already implemented
- Location: `widget/src/widget.ts`
- Function: `playAudioFromUrl()`
- Automatic: Plays audio when `audio_url` is present
- Fallback: Browser TTS if backend audio fails

**No additional implementation needed** - TTS is already working!

---

## 3. Complete Code Snippets

### Snippet 1: Full Chatbot with Model Selection and TTS

**Backend (Python/FastAPI)** - Already implemented:
```python
# See backend/app/main.py for full implementation
# Key functions:
# - get_models(): List available models
# - chat_completion_responses_api(): Chat with Responses API
# - generate_xai_tts_audio(): Generate TTS (already implemented)
```

**Frontend (JavaScript)** - Widget:
```javascript
// See widget/src/widget.ts for full implementation
// Key features:
// - Automatic audio playback when audio_url present
// - Browser TTS fallback
// - Voice input support (can be added)
```

### Snippet 2: Minimal Chatbot Example

**Python (Simple)**:
```python
import requests
import os

API_KEY = os.getenv('XAI_API_KEY')
BASE_URL = 'https://api.x.ai/v1'

def simple_chat(message, model='grok-4-1-fast-non-reasoning'):
    """Simple chat completion using Responses API"""
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'input': [
            {'role': 'user', 'content': message}
        ],
        'model': model,
        'store': True
    }
    
    response = requests.post(f'{BASE_URL}/responses', headers=headers, json=data)
    
    if response.status_code == 200:
        result = response.json()
        output = result['output'][0]
        text = output['content'][0]['text']
        response_id = result['id']
        
        return {
            'text': text,
            'response_id': response_id,
            'usage': result.get('usage', {})
        }
    
    raise Exception(f'Error: {response.status_code}')

# Usage
result = simple_chat("Hello! What is 2+2?")
print(f"Bot: {result['text']}")
print(f"Response ID: {result['response_id']}")
print(f"Tokens: {result['usage'].get('total_tokens', 0)}")
```

**JavaScript (Browser)**:
```javascript
const API_KEY = 'your_api_key';
const BASE_URL = 'https://api.x.ai/v1';

async function simpleChat(message, model = 'grok-4-1-fast-non-reasoning') {
  const response = await fetch(`${BASE_URL}/responses`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      input: [
        { role: 'user', content: message }
      ],
      model: model,
      store: true
    })
  });
  
  if (!response.ok) {
    throw new Error(`Error: ${response.status}`);
  }
  
  const data = await response.json();
  const output = data.output[0];
  const text = output.content[0].text;
  
  return {
    text: text,
    responseId: data.id,
    usage: data.usage
  };
}

// Usage
simpleChat("Hello! What is 2+2?")
  .then(result => {
    console.log('Bot:', result.text);
    console.log('Response ID:', result.responseId);
  })
  .catch(error => console.error('Error:', error));
```

### Snippet 3: Persistent Conversation with Response IDs

```python
def continue_conversation(previous_response_id, new_message, model='grok-4-1-fast-non-reasoning'):
    """Continue conversation using previous response ID"""
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'input': [
            {'role': 'user', 'content': new_message}
        ],
        'model': model,
        'previous_response_id': previous_response_id,  # Continue from here
        'store': True
    }
    
    response = requests.post(f'{BASE_URL}/responses', headers=headers, json=data)
    
    if response.status_code == 200:
        result = response.json()
        return {
            'text': result['output'][0]['content'][0]['text'],
            'response_id': result['id'],
            'usage': result.get('usage', {})
        }
    
    raise Exception(f'Error: {response.status_code}')

# Example: Multi-turn conversation
response1 = simple_chat("My name is Alice")
response_id = response1['response_id']

response2 = continue_conversation(response_id, "What's my name?")
print(f"Bot: {response2['text']}")  # Should remember: "Your name is Alice"
```

### Snippet 4: Streaming Responses

```python
import json

def stream_chat(messages, model='grok-4-1-fast-non-reasoning'):
    """Stream chat responses using SSE"""
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'input': messages,
        'model': model,
        'stream': True
    }
    
    response = requests.post(
        f'{BASE_URL}/responses',
        headers=headers,
        json=data,
        stream=True
    )
    
    if response.status_code == 200:
        full_text = ""
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data_str = line[6:]  # Remove 'data: ' prefix
                    if data_str.strip() == '[DONE]':
                        break
                    
                    try:
                        chunk = json.loads(data_str)
                        # Extract content from chunk
                        if 'output' in chunk:
                            # Handle streaming output
                            delta = chunk.get('delta', {})
                            if 'content' in delta:
                                text = delta['content']
                                full_text += text
                                print(text, end='', flush=True)
                    except json.JSONDecodeError:
                        continue
        
        print()  # New line after streaming
        return full_text
    
    raise Exception(f'Error: {response.status_code}')
```

---

## 4. Current Implementation Summary

### ✅ Already Implemented

1. **TTS Integration**: X.AI Grok Voice Agent API
   - Location: `backend/app/main.py`
   - Function: `generate_xai_tts_audio()`
   - Automatic: Works when provider is 'xai'
   - Output: Base64 WAV audio data URL

2. **Widget Audio Playback**: 
   - Location: `widget/src/widget.ts`
   - Function: `playAudioFromUrl()`
   - Automatic: Plays when `audio_url` present
   - Fallback: Browser TTS

3. **Chat Endpoint**:
   - Location: `backend/app/main.py`
   - Endpoint: `POST /api/chat`
   - Supports: X.AI, OpenAI, Anthropic
   - Model: `grok-4-1-fast-non-reasoning` (default)

### 🔄 Recommended Updates

1. **Migrate to Responses API**:
   - Current: Uses deprecated `/v1/chat/completions`
   - Recommended: Switch to `/v1/responses`
   - Benefits: Stateful conversations, latest features

2. **Model Selection**:
   - Current: `grok-4-1-fast-non-reasoning` ✅ (already updated)
   - Good: Latest fast model, low cost

3. **Add Voice Input** (Optional):
   - Could add STT to widget for voice input
   - Currently supports text input only

---

## 5. Quick Start Checklist

- [x] **TTS Implementation**: Complete (X.AI Voice Agent API)
- [x] **Widget Audio**: Complete (automatic playback)
- [x] **Chat Endpoint**: Complete (supports X.AI)
- [x] **Model Selection**: Complete (grok-4-1-fast-non-reasoning)
- [ ] **Migrate to Responses API**: Recommended for future
- [ ] **Voice Input (STT)**: Optional enhancement
- [ ] **Streaming**: Optional enhancement

---

## 6. Testing Your Implementation

### Test Basic Chat
```bash
curl -X POST https://your-api.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "your-client-id",
    "message": "Hello! What is 2+2?"
  }'
```

### Test TTS (automatic)
- Send message via widget
- Check browser console for `[TTS]` logs
- Should see: `[TTS] Successfully generated audio`
- Audio should play automatically

### Verify Model
- Check response includes `audio_url` (base64 data URL)
- Format: `data:audio/wav;base64,...`
- Browser should play audio automatically

---

## References

- X.AI TTS Implementation: `XAI_TTS_IMPLEMENTATION.md`
- X.AI Capabilities: `XAI_TOOLS_CAPABILITIES.md`
- X.AI API Reference: `XAI_API_REFERENCE.md`
- Current Implementation: `backend/app/main.py`
- Widget Code: `widget/src/widget.ts`

---

## Important Notes

1. **Chat Completions is Deprecated**: Use Responses API (`/v1/responses`) instead
2. **X.AI Has Native TTS**: Use Grok Voice Agent API (already implemented)
3. **Fast Models Recommended**: Use `grok-4-1-fast-non-reasoning` instead of `grok-4-0709`
4. **TTS is Automatic**: No additional code needed - backend handles it
5. **Widget Plays Audio**: Automatically when `audio_url` is present

All the heavy lifting is done - your chatbot already has working TTS via X.AI!
