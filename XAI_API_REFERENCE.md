# X.AI REST API Reference Summary

## Overview

X.AI provides a comprehensive REST API that is fully compatible with the OpenAI REST API format. All endpoints are located at `https://api.x.ai` and require authentication with `Authorization: Bearer <your xAI API key>`.

## Current Implementation Status

### ⚠️ Currently Used (Legacy)
- **`POST /v1/chat/completions`** - Used for chat responses (LEGACY/DEPRECATED)
  - Currently implemented in `backend/app/main.py`
  - Supports X.AI, OpenAI, and Anthropic providers
  - Returns text responses
  - **Note**: This endpoint is deprecated - Responses API is preferred

### ✅ Recommended Migration
- **`POST /v1/responses`** - Recommended endpoint (replaces Chat Completions)
  - Stateful conversations with response IDs
  - Stores responses for 30 days
  - Supports agentic tool calling
  - New features come to Responses API first

### 📋 Available for Future Use

## Core Endpoints

### Chat Completions (Deprecated)
- **`POST /v1/chat/completions`** - Create chat response (LEGACY)
  - ⚠️ **Deprecated**: Responses API is preferred
  - Text/image chat prompts
  - Supports streaming with `"stream": true`
  - Compatible with OpenAI format
  - **Migration**: Use `/v1/responses` instead

### Responses API (Recommended)
- **`POST /v1/responses`** - Create new response (stateful) ⭐ **PREFERRED**
  - ⭐ **Recommended**: New features come here first
  - Response ID can be used to continue conversation
  - Stores responses for 30 days
  - Supports agentic tool calling
  - Replaces deprecated Chat Completions endpoint
- **`GET /v1/responses/{response_id}`** - Retrieve previous response
- **`DELETE /v1/responses/{response_id}`** - Delete previous response

### Deferred Completions
- **`POST /v1/chat/completions`** (with deferred flag) - Create deferred request
- **`GET /v1/chat/deferred-completion/{request_id}`** - Get deferred result
  - Returns `202 Accepted` if still processing
  - Returns `200 OK` when ready
  - Result available for 24 hours (one-time access)

### Messages API
- **`POST /v1/messages`** - Anthropic-compatible messages endpoint
  - Same format as Anthropic API
  - Useful for compatibility

### Image Generation
- **`POST /v1/images/generations`** - Generate images from prompts
  - Model: `grok-2-image`
  - Returns image URLs or base64 data

## Model Management

### Model Information
- **`GET /v1/models`** - List all models (minimal info)
- **`GET /v1/models/{model_id}`** - Get model info (minimal)
- **`GET /v1/language-models`** - List language models (full info)
  - Includes pricing, modalities, aliases
- **`GET /v1/language-models/{model_id}`** - Get language model (full info)
- **`GET /v1/image-generation-models`** - List image generation models
- **`GET /v1/image-generation-models/{model_id}`** - Get image model info

### API Key Management (Consumer API)
- **`GET /v1/api-key`** - Get API key information
  - ACLs, status, team info
  - Returns information about the API key used in the request

### Management API (Enterprise)
The Management API allows programmatic management of teams, API keys, and access control. Base URL: `https://management-api.x.ai`

**Authentication**: Requires a management key (different from regular API keys)

#### API Key Management
- **`POST /auth/teams/{teamId}/api-keys`** - Create new API key
  - Requires: Team ID, API key name, ACLs
  - Returns: Full API key (only shown once), key ID, metadata
- **`GET /auth/teams/{teamId}/api-keys`** - List API keys
  - Returns: List of API keys (redacted) for team
  - Supports pagination and ACL filtering
- **`PUT /auth/api-keys/{apiKeyId}`** - Update API key
  - Can update: name, ACLs, rate limits (tpm, qpm, qps), expiration, disabled status
- **`DELETE /auth/api-keys/{apiKeyId}`** - Delete API key
  - Permanently deletes an API key
- **`GET /auth/api-keys/{apiKeyId}/propagation`** - Check API key propagation
  - Verifies if API key has propagated to inference clusters

#### Team Management
- **`GET /auth/teams/{teamId}/models`** - List models accessible by team
  - Returns: Available models per cluster with pricing, features, rate limits
- **`GET /auth/teams/{teamId}/endpoints`** - List possible endpoint ACLs
  - Returns: Available endpoint ACLs for API key permissions

#### Management Key Validation
- **`GET /auth/management-keys/validation`** - Validate management key
  - Returns: Management key information, team ID, scope, ACLs

**Use Cases**:
- Enterprise API key management
- Automated key rotation
- Team access control
- Rate limit management
- Multi-team deployments

## Utility Endpoints

### Tokenization
- **`POST /v1/tokenize-text`** - Tokenize text with specified model
  - Returns token IDs, string tokens, token bytes

## Response Formats

### Chat Completion Response
```json
{
  "id": "<completion_id>",
  "object": "chat.completion",
  "created": 1752854522,
  "model": "grok-4-0709",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "...",
        "refusal": null
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 32,
    "completion_tokens": 9,
    "total_tokens": 135,
    "prompt_tokens_details": {
      "text_tokens": 32,
      "audio_tokens": 0,
      "image_tokens": 0,
      "cached_tokens": 6
    },
    "completion_tokens_details": {
      "reasoning_tokens": 94,
      "audio_tokens": 0
    }
  }
}
```

### Response API Format
```json
{
  "id": "<response_id>",
  "object": "response",
  "created_at": 1754475266,
  "model": "grok-4-0709",
  "status": "completed",
  "output": [
    {
      "type": "message",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "..."
        }
      ]
    }
  ],
  "usage": {...}
}
```

## Available Models

### Language Models

#### Grok 4.1 Fast (Recommended for Agentic Tool Calling)
**Frontier multimodal model optimized for high-performance agentic tool calling**

| Model | Context | Rate Limits | Pricing (per million tokens) |
|-------|---------|-------------|------------------------------|
| `grok-4-1-fast-reasoning` | 2,000,000 | 4M tpm, 480 rpm | $0.20 (input) / $0.50 (output) |
| `grok-4-1-fast-non-reasoning` | 2,000,000 | 4M tpm, 480 rpm | $0.20 (input) / $0.50 (output) |

**Features**: Function calling, Structured outputs, Reasoning (reasoning version), Lightning fast, Low cost

#### Grok 4 Fast
| Model | Context | Rate Limits | Pricing (per million tokens) |
|-------|---------|-------------|------------------------------|
| `grok-4-fast-reasoning` | 2,000,000 | 4M tpm, 480 rpm | $0.20 (input) / $0.50 (output) |
| `grok-4-fast-non-reasoning` | 2,000,000 | 4M tpm, 480 rpm | $0.20 (input) / $0.50 (output) |

**Features**: Function calling, Structured outputs, Reasoning (reasoning version)

#### Grok 4
| Model | Context | Rate Limits | Pricing (per million tokens) |
|-------|---------|-------------|------------------------------|
| `grok-4-0709` | 256,000 | 2M tpm, 480 rpm | $3.00 (input) / $15.00 (output) |

**Features**: Text input/output, Image understanding

#### Grok 3
| Model | Context | Rate Limits | Pricing (per million tokens) |
|-------|---------|-------------|------------------------------|
| `grok-3` | 131,072 | 600 rpm | $3.00 (input) / $15.00 (output) |
| `grok-3-mini` | 131,072 | 480 rpm | $0.30 (input) / $0.50 (output) |

**Features**: Text input/output, Reasoning (grok-3-mini)

#### Grok 2
| Model | Context | Rate Limits | Pricing (per million tokens) |
|-------|---------|-------------|------------------------------|
| `grok-2-vision-1212` | 32,768 | 600 rpm | $2.00 (input) / $10.00 (output) |

**Features**: Text and image input, Text output

#### Grok Code Fast 1
| Model | Context | Rate Limits | Pricing (per million tokens) |
|-------|---------|-------------|------------------------------|
| `grok-code-fast-1` | 256,000 | 2M tpm, 480 rpm | $0.20 (input) / $1.50 (output) |

**Features**: Optimized for agentic coding tasks, Tool calling, 4x speed, 1/10th cost

### Image Generation Models

| Model | Rate Limits | Pricing |
|-------|-------------|---------|
| `grok-2-image-1212` | 300 rpm | $0.07 per image |

**Features**: Image generation from text prompts

## Model Selection Guide

### For Agentic Tool Calling
- **Recommended**: `grok-4-1-fast-reasoning` or `grok-4-1-fast-non-reasoning`
  - Optimized for agentic tool calling
  - 2M context window
  - Fast and low cost
  - Supports function calling, structured outputs

### For Coding Tasks
- **Recommended**: `grok-code-fast-1`
  - Optimized for agentic coding
  - 4x speed, 1/10th cost
  - Tool calling support
  - 256K context

### For General Chat
- **Recommended**: `grok-4-fast-reasoning` or `grok-4-fast-non-reasoning`
  - Fast responses
  - Low cost
  - 2M context window

### For Image Understanding
- **Recommended**: `grok-4-0709` or `grok-2-vision-1212`
  - Supports image input
  - Text output with image context

### For Image Generation
- **Recommended**: `grok-2-image-1212`
  - Generate images from text prompts
  - $0.07 per image

### For Cost-Effective Simple Tasks
- **Recommended**: `grok-3-mini`
  - Lowest cost option
  - $0.30/$0.50 per million tokens
  - Reasoning support

## Rate Limits

Rate limits are per model and per API key:

| Model Family | Rate Limits |
|-------------|-------------|
| Grok 4.1 Fast | 4M tokens/min, 480 requests/min |
| Grok 4 Fast | 4M tokens/min, 480 requests/min |
| Grok 4 | 2M tokens/min, 480 requests/min |
| Grok Code Fast | 2M tokens/min, 480 requests/min |
| Grok 3 | 600 requests/min |
| Grok 3 Mini | 480 requests/min |
| Grok 2 Vision | 600 requests/min |
| Grok 2 Image | 300 requests/min |

**View your rate limits**: https://console.x.ai

## Pricing Information

### Language Models (Per Million Tokens)

**Grok 4.1 Fast** (Recommended for Agentic):
- Input: $0.20 per million tokens
- Output: $0.50 per million tokens

**Grok 4 Fast**:
- Input: $0.20 per million tokens
- Output: $0.50 per million tokens

**Grok 4**:
- Input: $3.00 per million tokens
- Output: $15.00 per million tokens

**Grok Code Fast 1**:
- Input: $0.20 per million tokens
- Output: $1.50 per million tokens

**Grok 3**:
- Input: $3.00 per million tokens
- Output: $15.00 per million tokens

**Grok 3 Mini** (Cost-Effective):
- Input: $0.30 per million tokens
- Output: $0.50 per million tokens

**Grok 2 Vision**:
- Input: $2.00 per million tokens
- Output: $10.00 per million tokens

### Image Generation

**Grok 2 Image**:
- $0.07 per image output

### Pricing Details

Models expose pricing information via `/v1/language-models` endpoint:
- `prompt_text_token_price` - Price per 100M prompt tokens (cents)
- `completion_text_token_price` - Price per 100M completion tokens (cents)
- `cached_prompt_text_token_price` - Price for cached tokens (cents)
- `prompt_image_token_price` - Price per 100M image tokens (cents)
- `search_price` - Price per 100M searches (cents)

## System Fingerprint

### Overview
Each response from X.AI API includes a unique `system_fingerprint` value that identifies the current state of the backend system's configuration.

### Example Response
```json
{
  "id": "<completion_id>",
  "model": "grok-4",
  "system_fingerprint": "fp_6ca29cf396",
  ...
}
```

### Usage

**Monitoring System Changes**:
- The fingerprint acts as version control for backend configuration
- Changes when any part of the system changes (model parameters, server settings, infrastructure)
- Track system evolution over time for debugging and optimization
- Ensure consistency in API responses

**Security and Integrity**:
- Verify response integrity by comparing fingerprints
- Detect if data has been tampered with during transmission
- Verify service hasn't been compromised
- Note: Fingerprint changes over time (expected behavior)

**Compliance and Auditing**:
- Use as part of audit trail for regulated environments
- Show which configurations were in use at specific times
- Track system state changes for compliance purposes

### Implementation Notes
- Automatically included in all responses
- No additional configuration required
- Track along with token consumption and metrics
- Monitor for unexpected changes (may indicate system updates)

### Example Usage
```python
response = client.chat.create(...).sample()

# Track fingerprint along with usage
fingerprint = response.system_fingerprint
tokens = response.usage.total_tokens

# Log for monitoring/auditing
log_metrics(fingerprint, tokens, timestamp)
```

---

## Migration from Other Providers

### Overview
X.AI API is designed to be compatible with both OpenAI and Anthropic SDKs, making migration straightforward. The API follows OpenAI's format, so we recommend using the OpenAI SDK for better stability.

### Migration Steps

**Two Simple Steps**:
1. **Set base URL**: Change base URL to `https://api.x.ai/v1`
2. **Set API key**: Use your X.AI API key (obtained from xAI Console)
3. **Set model**: Use Grok model names (e.g., `grok-4`, `grok-3-fast`)

### OpenAI SDK Migration

**Python Example**:
```python
from openai import OpenAI

# Step 1 & 2: Set base URL and API key
client = OpenAI(
    api_key="your_xai_api_key",  # X.AI API key
    base_url="https://api.x.ai/v1",  # X.AI base URL
)

# Step 3: Use Grok model
completion = client.chat.completions.create(
    model="grok-4",  # Grok model name
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ]
)

print(completion.choices[0].message.content)
```

**JavaScript Example**:
```javascript
import OpenAI from 'openai';

const client = new OpenAI({
  apiKey: 'your_xai_api_key',  // X.AI API key
  baseURL: 'https://api.x.ai/v1',  // X.AI base URL
});

const completion = await client.chat.completions.create({
  model: 'grok-4',  // Grok model name
  messages: [
    { role: 'system', content: 'You are a helpful assistant.' },
    { role: 'user', content: 'Hello!' }
  ],
});

console.log(completion.choices[0].message.content);
```

### Anthropic SDK Migration

**Python Example**:
```python
from anthropic import Anthropic

# Step 1 & 2: Set base URL and API key
client = Anthropic(
    api_key="your_xai_api_key",  # X.AI API key
    base_url="https://api.x.ai",  # X.AI base URL (note: no /v1)
)

# Step 3: Use Grok model
message = client.messages.create(
    model="grok-4",  # Grok model name
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Hello!"}
    ]
)

print(message.content[0].text)
```

**Note**: Anthropic SDK uses `/v1/messages` endpoint format, which X.AI also supports.

### Third-Party Tools

**LangChain (Python)**:
```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="grok-4",
    openai_api_key="your_xai_api_key",
    openai_api_base="https://api.x.ai/v1",
)
```

**LangChain (JavaScript)**:
```javascript
import { ChatOpenAI } from "langchain/chat_models/openai";

const llm = new ChatOpenAI({
  modelName: "grok-4",
  openAIApiKey: "your_xai_api_key",
  configuration: {
    baseURL: "https://api.x.ai/v1",
  },
});
```

**Continue (VS Code Extension)**:
Update `.continue/config.json`:
```json
{
  "models": [{
    "title": "Grok",
    "provider": "openai",
    "model": "grok-4",
    "apiBase": "https://api.x.ai/v1",
    "apiKey": "your_xai_api_key"
  }]
}
```

### Compatibility Notes

**OpenAI SDK**:
- ✅ Full compatibility with OpenAI SDK
- ✅ Recommended for better stability
- ✅ Same request/response format
- ✅ Works with streaming, tools, etc.

**Anthropic SDK**:
- ✅ Compatible via `/v1/messages` endpoint
- ✅ Uses Anthropic message format
- ⚠️ Some features may differ

**Differences**:
- Model names: Use Grok model names (`grok-4`, `grok-3-fast`, etc.)
- Some capabilities: X.AI-specific features (agentic tools, etc.) may require xAI SDK
- Rate limits: X.AI rate limits (check console.x.ai)

### Available Grok Models

**Language Models**:
- `grok-4` (latest Grok-4)
- `grok-4-0709` (specific version)
- `grok-3-fast` (fast reasoning)
- `grok-3-mini` (mini model)
- `grok-code-fast-1` (code model)
- `grok-2-vision-1212` (vision model)

**Image Generation**:
- `grok-2-image` (image generation)

### Migration Checklist

- [ ] Get X.AI API key from https://console.x.ai
- [ ] Update base URL to `https://api.x.ai/v1` (OpenAI) or `https://api.x.ai` (Anthropic)
- [ ] Replace API key with X.AI API key
- [ ] Update model names to Grok models
- [ ] Test with simple request
- [ ] Update any model-specific configurations
- [ ] Check rate limits (may differ from other providers)
- [ ] Update error handling if needed

### Benefits of Migration

1. **Cost**: Potentially lower costs depending on usage
2. **Performance**: Fast reasoning models (grok-4-1-fast)
3. **Features**: Unique X.AI features (agentic tools, etc.)
4. **Compatibility**: Easy migration from OpenAI/Anthropic
5. **Innovation**: Access to latest Grok capabilities

---

## Integration Notes

### Current Implementation
The backend currently uses `POST /v1/chat/completions` for X.AI provider:
- Endpoint: `https://api.x.ai/v1/chat/completions`
- Authentication: `Authorization: Bearer {api_key}`
- Format: OpenAI-compatible request/response
- System fingerprint: Automatically included in responses

**Migration Support**:
- Already compatible with OpenAI format
- Easy to switch between providers
- Can use OpenAI SDK directly if desired

### Future Enhancements
1. **Responses API**: Could migrate to `/v1/responses` for stateful conversations
2. **Deferred Completions**: For long-running agentic queries
3. **Streaming**: Already supported via `"stream": true`
4. **Model Selection**: Dynamic model selection based on capabilities
5. **Fingerprint Tracking**: Log and monitor system fingerprints for auditing
6. **OpenAI SDK**: Could use OpenAI SDK directly for X.AI provider

## Authentication

All requests require:
```
Authorization: Bearer <your_xAI_API_key>
```

## Rate Limits

- View rate limits at: https://console.x.ai
- Deferred completions use same rate limit as chat completions
- Rate limits are per API key

## Management API

### Overview
The Management API allows programmatic management of teams, API keys, and access control. This is separate from the regular API and requires a management key.

**Base URL**: `https://management-api.x.ai`

**Authentication**: Management key (Bearer token in Authorization header)

### API Key Management Endpoints

#### Create API Key
```
POST /auth/teams/{teamId}/api-keys
```

**Request Body**:
```json
{
  "name": "My API key",
  "acls": [
    "api-key:endpoint:*",
    "api-key:model:*"
  ]
}
```

**Response**: Returns full API key (only shown once), key ID, metadata

#### List API Keys
```
GET /auth/teams/{teamId}/api-keys
```

**Query Parameters**:
- `pageSize`: Control page size
- `paginationToken`: Pagination token
- `aclFilters`: Filter by ACLs

**Response**: List of API keys (redacted) with metadata

#### Update API Key
```
PUT /auth/api-keys/{apiKeyId}
```

**Can Update**:
- Name
- ACLs
- Rate limits (tpm, qpm, qps)
- Expiration time
- Disabled status

**Request Body**:
```json
{
  "apiKey": {
    "tpm": "42000000"
  },
  "fieldMask": "tpm"
}
```

#### Delete API Key
```
DELETE /auth/api-keys/{apiKeyId}
```

**Warning**: Permanently deletes the API key

#### Check Propagation
```
GET /auth/api-keys/{apiKeyId}/propagation
```

**Response**: Map of inference clusters and propagation status

### Team Management Endpoints

#### List Team Models
```
GET /auth/teams/{teamId}/models
```

**Response**: Available models per cluster with:
- Pricing information
- Features (function calling, structured outputs, reasoning)
- Rate limits (rps, rpm, tpm)
- Context window sizes
- Aliases

#### List Endpoint ACLs
```
GET /auth/teams/{teamId}/endpoints
```

**Response**: Available endpoint ACLs:
- `api-key:endpoint:chat`
- `api-key:endpoint:embed`
- `api-key:endpoint:image`
- `api-key:endpoint:models`
- `api-key:endpoint:sample`
- `api-key:endpoint:tokenize`
- `api-key:endpoint:documents`
- `api-key:endpoint:*` (wildcard)

### ACL System

**Endpoint ACLs**:
- Format: `api-key:endpoint:{endpoint_name}`
- Examples: `api-key:endpoint:chat`, `api-key:endpoint:*`
- Controls which endpoints the API key can access

**Model ACLs**:
- Format: `api-key:model:{model_name}`
- Examples: `api-key:model:grok-4`, `api-key:model:*`
- Controls which models the API key can use

**Default Behavior**:
- API keys without ACLs fail all requests
- Use wildcards (`*`) for full access
- Can restrict to specific endpoints/models

### Use Cases

**Enterprise API Key Management**:
- Create keys programmatically for new customers
- Rotate keys automatically
- Manage team access control

**Rate Limit Management**:
- Set per-key rate limits (tpm, qpm, qps)
- Monitor and adjust limits dynamically

**Multi-Team Deployments**:
- Manage API keys across multiple teams
- Enforce access policies per team

**Access Control**:
- Restrict keys to specific endpoints
- Limit access to specific models
- Implement least-privilege access

### Example: Create API Key with Restrictions

```python
import requests

MANAGEMENT_KEY = "your_management_key"
TEAM_ID = "your_team_id"

# Create API key with specific permissions
response = requests.post(
    f"https://management-api.x.ai/auth/teams/{TEAM_ID}/api-keys",
    headers={
        "Authorization": f"Bearer {MANAGEMENT_KEY}",
        "Content-Type": "application/json"
    },
    json={
        "name": "Customer API Key",
        "acls": [
            "api-key:endpoint:chat",  # Only chat endpoint
            "api-key:model:grok-4-1-fast-non-reasoning"  # Specific model
        ],
        "tpm": "1000000",  # 1M tokens per minute
        "qpm": "100"  # 100 requests per minute
    }
)

api_key_data = response.json()
print(f"API Key: {api_key_data['apiKey']}")  # Only shown once!
print(f"Key ID: {api_key_data['apiKeyId']}")
```

### Security Considerations

- **Management keys**: Separate from regular API keys, more powerful
- **ACLs**: Use least-privilege access when possible
- **Key storage**: Store API keys securely, never expose in client code
- **Key rotation**: Implement regular key rotation for security
- **Monitoring**: Monitor API key usage and propagation

## References

- Full API Reference: https://docs.x.ai/docs/api-reference
- Management API: https://docs.x.ai/docs/api-reference/management-api
- Console: https://console.x.ai
- Models: https://docs.x.ai/docs/models
- API Keys: https://console.x.ai/team/default/api-keys
