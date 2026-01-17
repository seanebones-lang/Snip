# X.AI Agentic Tool Calling - Complete Capabilities Overview

## Summary

X.AI's Grok Voice Agent API and Agentic Tool Calling provide powerful capabilities beyond basic chat:

1. ✅ **TTS (Text-to-Speech)** - IMPLEMENTED
2. ✅ **Streaming Responses** - Available (built into SDK)
3. 📋 **Structured Outputs** - Available (type-safe JSON schemas)
4. 📋 **Deferred Chat Completions** - Available (async processing)
5. 📋 **Web Search** - Available for implementation
6. 📋 **X/Twitter Search** - Available for implementation
7. 📋 **Collections Search** - Available for implementation (alternative/complement to RAG)
8. 📋 **Code Execution** - Available for implementation
9. 📋 **Remote MCP Tools** - Available for implementation (custom tool integration)

## 1. TTS (Text-to-Speech) - ✅ IMPLEMENTED

**Status**: Complete and tested

**Implementation**: 
- Uses Grok Voice Agent API via WebSocket
- Generates audio in PCM format, converts to WAV
- Returns base64-encoded data URL
- Supports 5 voices: Ara, Leo, Rex, Sal, Eve

**Files Modified**:
- `backend/app/main.py` - TTS helper functions and chat endpoint integration
- `backend/requirements.txt` - Added `websockets==12.0`
- `backend/test_xai_tts.py` - Test script

**How It Works**:
1. Gets ephemeral token from X.AI
2. Connects via WebSocket to `wss://api.x.ai/v1/realtime`
3. Configures session with voice and audio format
4. Sends text, receives PCM audio chunks
5. Converts to WAV and base64-encodes for browser

---

## 2. Streaming Responses - ✅ Available

**What It Does**:
- Real-time streaming of text output as it's generated
- Server-Sent Events (SSE) for delta content delivery
- Enhanced user interaction with progressive text display
- Support for all text-output models (Chat, Image Understanding, etc.)

**Key Features**:
- Real-time feedback as text is generated
- Progressive display of response content
- Works with all text-output models
- Essential for reasoning models (longer response times)
- Critical for agentic tool calling (show progress in real-time)

**When to Use**:
- **Always recommended** for reasoning models (`grok-4-1-fast`)
- **Essential** for agentic tool calling (show tool calls in real-time)
- **Better UX** for any chat interface (users see progress)
- **Long responses** benefit from streaming (user doesn't wait)

**Implementation Requirements**:
1. Use `chat.stream()` instead of `chat.sample()`
2. Process chunks as they arrive: `for response, chunk in chat.stream()`
3. Display content progressively: `print(chunk.content, end="", flush=True)`
4. Set longer timeout for reasoning models: `timeout=3600`

**Basic Example**:
```python
from xai_sdk import Client
from xai_sdk.chat import user, system

client = Client(
    api_key=os.getenv('XAI_API_KEY'),
    timeout=3600,  # Longer timeout for reasoning models
)

chat = client.chat.create(model="grok-4")
chat.append(system("You are a helpful assistant."))
chat.append(user("What is the meaning of life?"))

# Stream response
for response, chunk in chat.stream():
    print(chunk.content, end="", flush=True)  # Progressive display
    # response.content auto-accumulates chunks

print(response.content)  # Full response available
```

**With Agentic Tool Calling**:
```python
from xai_sdk.tools import web_search, x_search

chat = client.chat.create(
    model="grok-4-1-fast",
    tools=[web_search(), x_search()],
    include=["verbose_streaming"],
)

chat.append(user("What's the latest news from xAI?"))

is_thinking = True
for response, chunk in chat.stream():
    # View tool calls as they happen
    for tool_call in chunk.tool_calls:
        print(f"\nCalling tool: {tool_call.function.name}")
    
    # Show thinking progress
    if response.usage.reasoning_tokens and is_thinking:
        print(f"\rThinking... ({response.usage.reasoning_tokens} tokens)", end="", flush=True)
    
    # Show content when ready
    if chunk.content and is_thinking:
        print("\n\nResponse:")
        is_thinking = False
    
    if chunk.content and not is_thinking:
        print(chunk.content, end="", flush=True)

# Final response with all data
print(f"\n\nCitations: {response.citations}")
print(f"Tool Usage: {response.server_side_tool_usage}")
```

**Event Stream Format**:
```
data: {
    "id":"<completion_id>",
    "object":"chat.completion.chunk",
    "created":<creation_time>,
    "model":"grok-4",
    "choices":[{"index":0,"delta":{"content":"Ah","role":"assistant"}}],
    "usage":{"prompt_tokens":41,"completion_tokens":1,...}
}
data: {
    "id":"<completion_id>",
    "choices":[{"index":0,"delta":{"content":",","role":"assistant"}}],
    ...
}
data: [DONE]
```

**Best Practices**:
1. **Always use streaming** for reasoning models (`grok-4-1-fast`)
2. **Set longer timeout** for reasoning models: `timeout=3600` (1 hour)
3. **Use SDK clients** to parse event streams (don't parse manually)
4. **Show progress indicators** for tool calls and reasoning
5. **Display chunks progressively** for better UX
6. **Access full response** after streaming: `response.content`

**Benefits**:
- **Real-time feedback**: Users see text as it's generated
- **Better UX**: No waiting for complete response
- **Progress visibility**: Show tool calls and reasoning progress
- **Reduced perceived latency**: Feels faster even if same total time
- **Essential for tools**: See tool calls happen in real-time

**Limitations**:
- Not supported for image generation models
- Requires SSE (Server-Sent Events) support
- May need longer timeouts for complex queries

**Use Cases**:
1. **Chat interfaces**: Progressive text display
2. **Agentic tool calling**: Show tool calls in real-time
3. **Reasoning models**: Show thinking progress
4. **Long responses**: Better perceived performance
5. **Interactive apps**: Real-time feedback

---

## 3. Structured Outputs - 📋 Available

**What It Does**:
- Return responses in specific, organized formats (JSON schemas)
- Guarantee responses match your input schema
- Type-safe, parseable output using Pydantic or Zod
- Perfect for document parsing, entity extraction, report generation

**Key Features**:
- **Type-safe output**: Responses guaranteed to match schema
- **Schema validation**: Automatic validation against your schema
- **Supported types**: string, number, integer, float, object, array, boolean, enum, anyOf
- **Pydantic/Zod support**: Use familiar schema tools
- **Combines with tools**: Works with agentic tool calling and function calling

**Supported Models**:
- All language models later than `grok-2-1212` and `grok-2-vision-1212`
- Structured outputs with tools: Grok 4 family only (`grok-4-1-fast`, `grok-4-fast`, etc.)

**When to Use**:
- **Document parsing**: Extract structured data from unstructured text
- **Entity extraction**: Extract specific entities from text
- **Report generation**: Generate consistent, structured reports
- **Data extraction**: Extract data from invoices, forms, contracts
- **Type-safe APIs**: Ensure API responses match expected schemas

**Basic Example**:
```python
from pydantic import BaseModel, Field
from xai_sdk import Client
from xai_sdk.chat import user

class Invoice(BaseModel):
    vendor_name: str = Field(description="Name of the vendor")
    invoice_number: str = Field(description="Unique invoice identifier")
    total_amount: float = Field(description="Total amount due", ge=0)
    line_items: list[LineItem] = Field(description="List of items")

client = Client(api_key=os.getenv("XAI_API_KEY"))
chat = client.chat.create(model="grok-4")
chat.append(user("Parse this invoice: ..."))

# Automatic parsing - returns tuple (Response, Invoice)
response, invoice = chat.parse(Invoice)

# Type-safe access
print(invoice.vendor_name)
print(invoice.total_amount)
assert isinstance(invoice, Invoice)  # Type-safe!
```

**Alternative: Using `response_format`**:
```python
# Pass schema to response_format
chat = client.chat.create(
    model="grok-4",
    response_format=Invoice,  # Pass Pydantic model
)

# Use sample() or stream()
response = chat.sample()

# Manual parsing
invoice = Invoice.model_validate_json(response.content)
```

**With Agentic Tools**:
```python
from xai_sdk.tools import web_search

class ProofInfo(BaseModel):
    name: str = Field(description="Name of the proof")
    authors: str = Field(description="Authors")
    year: str = Field(description="Year published")

chat = client.chat.create(
    model="grok-4-1-fast",  # Grok 4 family required
    tools=[web_search()],
)
chat.append(user("Find the latest machine-checked proof of four color theorem."))

# Structured output with tool calling
response, proof = chat.parse(ProofInfo)
print(f"Name: {proof.name}")
print(f"Authors: {proof.authors}")
```

**With Client-side Tools**:
```python
# Handle tool calls, then parse structured output
while True:
    response = chat.sample()
    if not response.tool_calls:
        break
    # Execute tools...
    
# Parse final response
response, result = chat.parse(CollatzResult)
```

**Streaming with Structured Outputs**:
```python
# Use stream() with response_format
chat = client.chat.create(
    model="grok-4",
    response_format=Summary,
)

# Stream JSON progressively
for response, chunk in chat.stream():
    print(chunk.content, end="", flush=True)

# Parse complete JSON
summary = Summary.model_validate_json(response.content)
```

**Supported Schema Types**:
- ✅ `string` (minLength/maxLength not supported)
- ✅ `number` (integer, float)
- ✅ `object`
- ✅ `array` (minItems/maxItems not supported)
- ✅ `boolean`
- ✅ `enum`
- ✅ `anyOf`
- ❌ `allOf` (not supported yet)

**Best Practices**:
1. **Use Pydantic**: Define schemas with Pydantic models
2. **Provide descriptions**: Use `Field(description="...")` for clarity
3. **Set constraints**: Use `ge`, `le`, `gt`, `lt` for validation
4. **Combine with tools**: Use structured outputs with agentic tool calling
5. **Handle errors**: Validate parsed output matches schema

**Benefits**:
- **Type safety**: Guaranteed schema matching
- **Easier parsing**: Automatic parsing with `parse()` method
- **Validation**: Built-in schema validation
- **Tool integration**: Works with agentic and client-side tools
- **Streaming support**: Can stream structured JSON

**Use Cases**:
1. **Invoice parsing**: Extract invoice data from text
2. **Document extraction**: Extract structured data from documents
3. **Entity extraction**: Extract specific entities (names, dates, amounts)
4. **Report generation**: Generate structured reports
5. **API responses**: Type-safe API response formats
6. **Data transformation**: Convert unstructured to structured data

**Combining with Tools**:
- ✅ **Agentic tools**: Web search, X search, code execution
- ✅ **Client-side tools**: Custom function calling
- ✅ **Collections search**: Search docs and return structured results
- ✅ **MCP tools**: Custom tools with structured output

**Example Use Cases**:
- Parse invoices and extract line items, amounts, dates
- Extract contact information from business cards
- Generate structured summaries of documents
- Extract data from contracts and legal documents
- Create type-safe API responses from natural language

---

## 4. Deferred Chat Completions - 📋 Available

**What It Does**:
- Create a chat completion request and get a `request_id`
- Retrieve the response later (within 24 hours)
- Poll for completion results asynchronously
- Perfect for long-running queries or background processing

**Key Features**:
- Asynchronous processing: Submit request, get ID, retrieve later
- 24-hour availability: Result available exactly once within 24 hours
- Polling support: SDK handles polling automatically
- Same rate limits as regular chat completions
- Supports reasoning content (for models that provide it)

**When to Use**:
- **Long-running queries**: Complex agentic tool calling that takes time
- **Background processing**: Fire-and-forget requests
- **Batch operations**: Submit multiple requests, retrieve later
- **Rate limit management**: Spread out response retrieval
- **Asynchronous workflows**: Don't wait for immediate response

**Implementation Requirements**:
1. Use `chat.defer()` instead of `chat.sample()` or `chat.stream()`
2. Specify timeout and polling interval
3. SDK automatically polls until result is ready
4. Retrieve result within 24 hours (one-time access)

**Basic Example**:
```python
from xai_sdk import Client
from xai_sdk.chat import user, system
from datetime import timedelta

client = Client(api_key=os.getenv('XAI_API_KEY'))

chat = client.chat.create(
    model="grok-4",
    messages=[system("You are a helpful assistant.")]
)
chat.append(user("What is 126/3?"))

# Defer completion - poll every 10 seconds for max 10 minutes
response = chat.defer(
    timeout=timedelta(minutes=10),
    interval=timedelta(seconds=10)
)

# Result is ready
print(response.content)
```

**With Agentic Tools**:
```python
from xai_sdk.tools import web_search, code_execution

chat = client.chat.create(
    model="grok-4-1-fast",
    tools=[web_search(), code_execution()],
)

chat.append(user("Analyze the top 5 companies by market cap and calculate correlations"))

# Defer for long-running agentic analysis
response = chat.defer(
    timeout=timedelta(minutes=30),  # Longer timeout for agentic tools
    interval=timedelta(seconds=15)
)

# Access full response with tool calls and citations
print(response.content)
print(response.citations)
print(response.server_side_tool_usage)
```

**Manual Polling** (if needed):
```python
# Submit deferred request
request_response = chat.defer_submit()  # Returns request_id

# Poll manually
import time
request_id = request_response['request_id']
max_wait = 600  # 10 minutes
poll_interval = 10  # 10 seconds

start_time = time.time()
while time.time() - start_time < max_wait:
    response = client.chat.get_deferred_completion(request_id)
    if response.status_code == 200:
        # Result is ready
        result = response.json()
        print(result['choices'][0]['message']['content'])
        break
    elif response.status_code == 202:
        # Still processing
        time.sleep(poll_interval)
    else:
        # Error
        raise Exception(f"Unexpected status: {response.status_code}")
```

**Response Format**:
Same as regular chat completion response:
```json
{
  "id": "<completion_id>",
  "object": "chat.completion",
  "created": 1752077400,
  "model": "grok-4",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "...",
        "reasoning_content": "..."  // If available
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 26,
    "completion_tokens": 168,
    "total_tokens": 498,
    ...
  }
}
```

**Best Practices**:
1. **Set appropriate timeout**: Based on query complexity
2. **Use reasonable polling interval**: Balance responsiveness vs. API calls
3. **Handle 202 responses**: Still processing, retry later
4. **Retrieve within 24 hours**: Result discarded after 24 hours
5. **One-time access**: Result can only be retrieved once

**Benefits**:
- **Non-blocking**: Submit request and continue processing
- **Long-running queries**: Perfect for complex agentic tool calling
- **Rate limit friendly**: Retrieve responses at convenient times
- **Batch processing**: Submit multiple requests, retrieve later
- **Background jobs**: Fire-and-forget pattern

**Limitations**:
- **24-hour availability**: Result discarded after 24 hours
- **One-time access**: Can only retrieve result once
- **No streaming**: Deferred completions don't support streaming
- **Rate limits**: Same as regular chat completions

**Use Cases**:
1. **Complex agentic queries**: Long-running research tasks
2. **Background processing**: Fire-and-forget requests
3. **Batch operations**: Submit multiple requests
4. **Rate limit management**: Spread out response retrieval
5. **Asynchronous workflows**: Don't block on response

**API Endpoints**:
- Submit: `POST /v1/chat/completions` with deferred flag
- Retrieve: `GET /v1/chat/deferred-completion/{request_id}`
- Response: `202 Accepted` (processing) or `200 OK` (ready)

**Rate Limits**:
- Same rate limit as regular chat completions
- View limits at: https://console.x.ai

---

## 5. Web Search - 📋 Available

**What It Does**:
- Real-time web search across the internet
- Browse web pages for context
- Image understanding (optional)
- Domain filtering (allowed/excluded domains)

**Key Features**:
- Automatic iterative search queries
- Citation tracking (all citations + inline citations)
- Image analysis when `enable_image_understanding=True`
- Domain restrictions for focused searches

**When to Use**:
- Current events and news
- Real-time information lookup
- Web page analysis
- Fact-checking and verification

**Implementation Requirements**:
1. Add `xai-sdk>=1.3.1` to requirements.txt
2. Use `grok-4-1-fast` model (optimized for search)
3. Enable via: `tools=[web_search()]`
4. Handle streaming for real-time tool call visibility
5. Process `response.citations` and `response.inline_citations`

**Example Configuration**:
```python
from xai_sdk.tools import web_search

# Basic web search
tools=[web_search()]

# With domain restrictions
tools=[web_search(allowed_domains=["wikipedia.org"])]

# With image understanding
tools=[web_search(enable_image_understanding=True)]
```

---

## 6. X/Twitter Search - 📋 Available

**What It Does**:
- Search X/Twitter posts, users, and threads
- Keyword search, semantic search, user search
- Thread fetching
- Video understanding (optional)

**Key Features**:
- Multiple search modes (Latest, Top, etc.)
- Handle filtering (allowed/excluded handles)
- Date range filtering
- Video analysis when `enable_video_understanding=True`

**When to Use**:
- Social media sentiment analysis
- Latest updates from specific accounts
- Trending topics research
- User and thread exploration

**Implementation Requirements**:
1. Add `xai-sdk>=1.3.1` to requirements.txt
2. Use `grok-4-1-fast` model
3. Enable via: `tools=[x_search()]`
4. Handle streaming responses
5. Process citations for X URLs

**Example Configuration**:
```python
from xai_sdk.tools import x_search
from datetime import datetime

# Basic X search
tools=[x_search()]

# With handle filtering
tools=[x_search(allowed_x_handles=["elonmusk", "xai"])]

# With date range
tools=[x_search(
    from_date=datetime(2025, 1, 1),
    to_date=datetime(2025, 1, 31)
)]

# With video understanding
tools=[x_search(enable_video_understanding=True)]
```

---

## 7. Collections Search - 📋 Available

**What It Does**:
- Search through uploaded knowledge bases (collections)
- Semantic search across your proprietary documents
- Multi-document synthesis and analysis
- Works with PDFs, text files, CSVs, and other formats

**Key Features**:
- Document retrieval from uploaded collections
- Semantic search (meaning-based, not just keywords)
- Multi-document reasoning and synthesis
- Citation tracking with `collections://` URIs
- Can combine with web search for hybrid analysis

**When to Use**:
- Enterprise knowledge bases
- Financial analysis (SEC filings, reports)
- Customer support chatbots with product docs
- Research and due diligence
- Compliance and legal document analysis
- Personal knowledge management

**Relation to Existing RAG**:
- **Current**: You have RAG using ChromaDB for premium clients
- **Collections Search**: X.AI's managed collections alternative
- **Comparison**:
  - **Your RAG**: Client manages ChromaDB, full control, local storage
  - **Collections Search**: X.AI manages, simpler setup, cloud-hosted
  - **Best Use**: Collections Search for easier setup, your RAG for full control

**Implementation Requirements**:
1. Add `xai-sdk>=1.4.0` to requirements.txt
2. Use `grok-4-1-fast` model (reasoning model)
3. Create collections via SDK
4. Upload documents to collections
5. Enable via: `tools=[collections_search(collection_ids=[...])]`
6. Handle streaming responses
7. Process `collections://` citation URIs

**Example Configuration**:
```python
from xai_sdk.tools import collections_search

# Basic collections search
tools=[collections_search(collection_ids=["collection-id-1"])]

# Multiple collections
tools=[collections_search(collection_ids=["collection-id-1", "collection-id-2"])]

# Combined with other tools
tools=[
    collections_search(collection_ids=["collection-id"]),
    web_search(),
    code_execution(),
]
```

**Citation Format**:
- `collections://collection_id/files/file_id`
- Example: `collections://collection_abc123/files/file_xyz789`

**Best Practices**:
- Upload documents to collections before searching
- Wait for documents to be processed (check status)
- Use semantic queries (natural language, not just keywords)
- Combine with web search for hybrid analysis
- Enable code execution for calculations on extracted data

**Use Cases**:
1. **Financial Analysis**: SEC filings, earnings reports, financial statements
2. **Customer Support**: Product documentation, FAQ, policy documents
3. **Research**: Academic papers, technical reports, industry analyses
4. **Compliance**: Official guidelines, regulations, policy documents
5. **Knowledge Management**: Personal/professional document collections

**Hybrid Search Pattern**:
Combine collections search with web search for powerful analysis:
- Internal data from collections + External market intelligence
- Proprietary docs + Real-time information
- Your documents + Current events and sentiment

**Implementation Steps**:
1. Create collection via SDK
2. Upload documents (PDF, text, CSV, etc.)
3. Wait for processing completion
4. Enable collections_search tool with collection IDs
5. Ask questions - Grok autonomously searches collections
6. Process citations and tool outputs

---

## 5. Code Execution - 📋 Available

**What It Does**:
- Write and execute Python code in real-time
- Mathematical computations and statistical analysis
- Data processing and visualization
- Financial modeling and calculations

**Key Features**:
- Sandboxed Python environment
- Pre-installed libraries (NumPy, Pandas, Matplotlib, SciPy)
- Real-time code generation and execution
- Automatic verification of results

**When to Use**:
- Complex calculations and formulas
- Data analysis and visualization
- Statistical computations
- Financial modeling
- Scientific simulations

**Use Cases**:
1. **Financial Analysis**: Portfolio optimization, risk calculations, option pricing
2. **Statistical Analysis**: Hypothesis testing, regression, probability distributions
3. **Scientific Computing**: Simulations, numerical methods, equation solving
4. **Data Processing**: Complex data transformations and analysis

**Implementation Requirements**:
1. Add `xai-sdk>=1.3.1` to requirements.txt
2. Use `grok-4-1-fast` model (reasoning model)
3. Enable via: `tools=[code_execution()]`
4. Use lower temperature (0.0-0.3) for mathematical accuracy
5. Handle streaming for real-time code execution visibility

**Example Configuration**:
```python
from xai_sdk.tools import code_execution

# Basic code execution
chat = client.chat.create(
    model="grok-4-1-fast",
    tools=[code_execution()],
    temperature=0.2,  # Lower for accuracy
)

# Use cases
chat.append(user("Calculate compound interest for $10,000 at 5% for 10 years"))
chat.append(user("Perform t-test comparing Group A [23,25,28,30] vs Group B [20,22,24,26]"))
chat.append(user("Analyze this sales data: [120000, 135000, 98000, 156000]"))
```

**Best Practices**:
- Be specific in requests (clear instructions)
- Provide context and data format
- Use lower temperature for calculations
- Specify requirements clearly

**Limitations**:
- Execution time constraints for complex computations
- Memory limitations for large datasets
- No external network access
- No persistent file system (stateless)
- Sandboxed environment for security

---

## Advanced Usage Patterns

### 1. Mixing Server-Side and Client-Side Tools

**What It Does**:
- Combine server-side agentic tools (web search, code execution) with custom client-side tools
- Leverage model's reasoning with server-side tools while adding local functionality
- Create powerful hybrid workflows

**How It Works**:
1. Define client-side tools using standard function calling patterns
2. Include both server-side and client-side tools in request
3. xAI automatically executes server-side tools
4. When model calls client-side tools, execution pauses
5. Execute client-side tools locally, append results back
6. Continue until final response (no more client-side calls)

**Example Use Case**:
- Server-side: Web search to find NBA champion
- Client-side: Get weather for champion's city (requires local database/API)

**Implementation Requirements**:
1. Use `xai-sdk>=1.4.0` (required for client-side tools)
2. Use `get_tool_call_type()` to identify client-side vs server-side
3. Handle tool loop: detect client-side calls → execute → append results → continue

**Example**:
```python
from xai_sdk.tools import web_search, get_tool_call_type
from xai_sdk.chat import tool, tool_result

# Define client-side tool
tools = [
    web_search(),  # Server-side
    tool(
        name="get_weather",
        description="Get weather for a city",
        parameters={...}
    )  # Client-side
]

# Tool loop
while True:
    client_side_tool_calls = []
    for response, chunk in chat.stream():
        for tool_call in chunk.tool_calls:
            if get_tool_call_type(tool_call) == "client_side_tool":
                client_side_tool_calls.append(tool_call)
            else:
                print(f"Server-side: {tool_call.function.name}")
    
    if not client_side_tool_calls:
        break  # Done
    
    # Execute client-side tools
    for tool_call in client_side_tool_calls:
        result = execute_client_tool(tool_call)
        chat.append(tool_result(result))
```

**Key Points**:
- `max_turns` only limits server-side tool turns per request
- Client-side tool calls act as "checkpoints" that reset turn counter
- Each client-side tool invocation creates a new request

### 2. Multi-turn Conversations with State Preservation

**What It Does**:
- Maintain context across multiple turns in agentic conversations
- Preserve full history: reasoning, tool calls, tool responses
- Build upon previous research for complex, iterative problem-solving

**Two Methods**:

**Method 1: Store History Remotely**
```python
# First turn
chat = client.chat.create(
    model="grok-4-1-fast",
    tools=[web_search(), x_search()],
    store_messages=True,  # Store on xAI servers
)
chat.append(user("What is xAI?"))
response = chat.sample()

# Second turn - continue from previous
chat = client.chat.create(
    model="grok-4-1-fast",
    tools=[web_search(), x_search()],
    previous_response_id=response.id,  # Continue from here
)
chat.append(user("What is its latest mission?"))
```

**Method 2: Encrypted Content (ZDR - Zero Data Retention)**
```python
# First turn
chat = client.chat.create(
    model="grok-4-1-fast",
    tools=[web_search(), x_search()],
    use_encrypted_content=True,  # Return encrypted state
)
chat.append(user("What is xAI?"))
response = chat.sample()
chat.append(response)  # Append encrypted state

# Second turn - continue with encrypted state
chat.append(user("What is its latest mission?"))
response = chat.sample()
```

**Benefits**:
- Full context preservation across turns
- Model can build upon previous research
- Tool call history maintained
- Reasoning state preserved

### 3. Tool Combinations

**Recommended Patterns**:

| Use Case | Tool Combination | Reason |
|----------|-----------------|--------|
| Research & Analyze | Web Search + Code Execution | Search gathers info, code analyzes/visualizes |
| Aggregate News | Web Search + X Search | Coverage from web and social |
| Extract Insights | Web Search + X Search + Code Execution | Collect data, compute correlations |
| Monitor Discussions | X Search + Web Search | Track sentiment + authoritative info |

**Example Combinations**:
```python
from xai_sdk.tools import web_search, x_search, code_execution

# Research setup
research_tools = [web_search(), code_execution()]

# News aggregation
news_tools = [web_search(), x_search()]

# Comprehensive analysis
comprehensive_tools = [web_search(), x_search(), code_execution()]

# Collections + Web (hybrid)
hybrid_tools = [
    collections_search(collection_ids=[...]),
    web_search(),
]
```

**When to Combine**:
- Need both internal and external data → Collections + Web Search
- Need data analysis → Add Code Execution
- Need real-time + social sentiment → Web + X Search
- Need comprehensive coverage → All search tools

### 4. Using Images in Context

**What It Does**:
- Include images in tool-enabled conversations
- Enable visual analysis with search tools
- Combine image understanding with web/X search

**Use Cases**:
- Identify objects in images and search for information
- Analyze visual content and find related resources
- Combine image understanding with research

**Example**:
```python
from xai_sdk.chat import image, user
from xai_sdk.tools import web_search, x_search

chat = client.chat.create(
    model="grok-4-1-fast",
    tools=[web_search(), x_search()],
)

# Add image to conversation
chat.append(
    user(
        "Search the internet and tell me what kind of dog is in this image.",
        "What is the typical lifespan of this breed?",
        image("https://example.com/dog.jpg"),
    )
)

# Model will:
# 1. Analyze the image
# 2. Identify the dog breed
# 3. Search web/X for breed information
# 4. Provide comprehensive answer with citations
```

**Image Formats Supported**:
- JPEG/JPG
- PNG
- URLs (web-accessible images)
- Base64-encoded images

**Combining with Tools**:
- Image + Web Search: Identify and research
- Image + X Search: Find social media discussions
- Image + Collections Search: Find similar in your docs
- Image + Code Execution: Analyze image data

---

## Implementation Roadmap

### Phase 1: TTS ✅ COMPLETE
- [x] WebSocket connection to X.AI
- [x] Audio generation and conversion
- [x] Base64 encoding for browser
- [x] Error handling and fallback
- [x] Test script

### Phase 2: Search Tools (Recommended)
**Priority**: High - Enables real-time information lookup

**Steps**:
1. Add `xai-sdk>=1.3.1` dependency
2. Refactor chat endpoint to use SDK for X.AI provider
3. Add client config options:
   - `enable_web_search` (Boolean)
   - `enable_x_search` (Boolean)
   - `search_filters` (JSON)
4. Use `grok-4-1-fast` model when search enabled
5. Handle streaming responses
6. Process and return citations
7. Add to premium tier (higher cost feature)

**Benefits**:
- Real-time information access
- Current events and news
- Social media insights
- Enhanced user experience

### Phase 3: Collections Search (Alternative/Complement to RAG)
**Priority**: Medium - Alternative to existing ChromaDB RAG

**Current State**:
- ✅ Premium clients have RAG using ChromaDB
- ✅ Documents uploaded via `/api/documents` endpoint
- ✅ Vector embeddings stored locally in ChromaDB
- ✅ Context retrieval in chat endpoint

**X.AI Collections Search**:
- Cloud-hosted collections (X.AI manages)
- Simpler setup (no ChromaDB configuration)
- Integrated with agentic tool calling
- Can combine with web search for hybrid analysis
- Citation format: `collections://collection_id/files/file_id`

**Comparison**:
| Feature | Your RAG (ChromaDB) | X.AI Collections |
|---------|-------------------|-----------------|
| Setup | Manual (ChromaDB setup) | Automatic (X.AI manages) |
| Storage | Local/self-hosted | Cloud-hosted |
| Control | Full control | Managed service |
| Cost | Infrastructure costs | X.AI API pricing |
| Integration | Custom retrieval | Native tool calling |
| Multi-tool | N/A | Can combine with web/search |
| Citations | Manual | Automatic `collections://` |

**Recommendation**:
- **Keep your RAG**: For clients who want full control and local storage
- **Add Collections**: As optional alternative for easier setup
- **Hybrid**: Use Collections for hybrid search (internal + external)

**Steps**:
1. Add `xai-sdk>=1.4.0` dependency
2. Add collection management endpoints:
   - `POST /api/collections` - Create collection
   - `POST /api/collections/{id}/documents` - Upload to collection
   - `GET /api/collections/{id}` - Get collection status
3. Add client config: `use_xai_collections` (Boolean)
4. Enable collections_search tool when using X.AI provider
5. Sync with existing document upload workflow

### Phase 4: Remote MCP Tools (Enterprise)
**Priority**: Medium - Powerful for enterprise integrations

**What It Does**:
- Connect to external MCP servers for custom tool integration
- Extend capabilities with third-party or custom tools
- Support multiple MCP servers simultaneously
- Access control via tool filtering

**Steps**:
1. Add `xai-sdk>=1.4.0` dependency
2. Add client config: `mcp_servers` (JSON array)
3. Add MCP server management endpoints:
   - `POST /api/mcp-servers` - Register MCP server
   - `GET /api/mcp-servers` - List registered servers
   - `DELETE /api/mcp-servers/{id}` - Remove server
4. Enable `mcp()` tools based on client config
5. Handle tool filtering and access control
6. Add to premium tier or enterprise feature

**Benefits**:
- Custom tool integrations
- Enterprise system connectivity
- Flexible extensibility
- Multi-server support

**Use Cases**:
- CRM integration (Salesforce, HubSpot)
- Database access
- API integrations
- Custom business logic
- Legacy system integration

### Phase 5: Code Execution (Optional)
**Priority**: Medium - Useful for mathematical/data tasks

**Steps**:
1. Add code execution tool option
2. Add client config: `enable_code_execution` (Boolean)
3. Use lower temperature for code tasks
4. Handle code execution outputs
5. Add to premium tier (high compute cost)

**Benefits**:
- Complex calculations
- Data analysis
- Financial modeling
- Enhanced problem-solving

---

## SDK Comparison

| Feature | Current (REST API) | With SDK (Agentic) |
|---------|-------------------|-------------------|
| Basic Chat | ✅ Works | ✅ Works |
| TTS | ✅ WebSocket | ✅ WebSocket |
| Web Search | ❌ Not available | ✅ Available |
| X Search | ❌ Not available | ✅ Available |
| Code Execution | ❌ Not available | ✅ Available |
| Collections Search | ❌ Not available | ✅ Available |
| Remote MCP Tools | ❌ Not available | ✅ Available |
| Citations | ❌ Not available | ✅ Available |
| Streaming | ❌ Not available | ✅ Full support (SSE) |
| Structured Outputs | ❌ Not available | ✅ Available (Pydantic/Zod) |
| Deferred Completions | ❌ Not available | ✅ Available (REST/SDK) |
| Model | grok-3-fast | grok-4-1-fast (optimized) |

---

## Migration Path

To add search or code execution tools:

1. **Add SDK dependency**:
   ```bash
   pip install xai-sdk>=1.3.1
   ```

2. **Update requirements.txt**:
   ```
   xai-sdk>=1.3.1
   ```

3. **Refactor chat endpoint**:
   - Use SDK for X.AI provider instead of direct REST calls
   - Conditionally enable tools based on client config
   - Handle streaming responses
   - Process citations and tool outputs

4. **Add client configuration**:
   - Database migration for new config fields
   - Dashboard UI for enabling tools
   - Pricing tier consideration (premium feature)

5. **Testing**:
   - Test with various queries
   - Verify citations are returned
   - Check streaming works correctly
   - Monitor token usage and costs

---

## Cost Considerations

**Tool Usage Pricing** (from X.AI):
- Token usage: Standard model pricing
- Tool invocations: Additional cost per tool call
- Search tools: Higher token usage (web browsing)
- Code execution: Higher compute costs

**Recommendations**:
- **Search**: Premium tier feature (higher cost, more value)
- **Collections Search**: Premium tier alternative to RAG (easier setup)
- **Code Execution**: Premium tier or add-on (high compute cost)
- **TTS**: Can remain basic tier (lower incremental cost)

---

## Next Steps

1. ✅ **TTS Implementation** - Complete and tested
2. ✅ **Streaming Responses** - Available via SDK (built-in)
3. 📋 **Structured Outputs** - Available for type-safe responses
4. 📋 **Deferred Completions** - Available for async processing
2. 📋 **Decide on Search Tools** - Should we implement?
3. 📋 **Decide on Collections Search** - Alternative/complement to existing RAG?
4. 📋 **Decide on Remote MCP Tools** - Should we implement for enterprise clients?
5. 📋 **Decide on Code Execution** - Should we implement?
6. 📋 **Client Configuration** - UI for enabling tools
7. 📋 **Pricing Strategy** - Tier features and costs

---

## Advanced Patterns Summary

### Pattern 1: Hybrid Server + Client Tools
- **When**: Need both agentic capabilities and local execution
- **Tools**: Server-side (web_search) + Client-side (custom functions)
- **Use Case**: Web search + local database queries, API calls

### Pattern 2: Multi-turn State Preservation
- **When**: Complex iterative research requiring context
- **Methods**: Remote storage (`store_messages=True`) or Encrypted (`use_encrypted_content=True`)
- **Use Case**: Building upon previous research across multiple turns

### Pattern 3: Tool Combinations
- **Research**: Web Search + Code Execution
- **News**: Web Search + X Search
- **Comprehensive**: All search tools + Code Execution
- **Hybrid**: Collections Search + Web Search

### Pattern 4: Image-Enhanced Conversations
- **When**: Visual analysis combined with research
- **Tools**: Image input + Search tools
- **Use Case**: Identify objects, analyze content, research related info

### Pattern 5: Asynchronous Request Processing
- **When**: Processing hundreds or thousands of requests
- **Method**: Use `AsyncClient` for concurrent requests
- **Use Case**: Batch processing, parallel queries, improved throughput

**What It Does**:
- Process multiple requests concurrently instead of sequentially
- Significantly reduce overall execution time
- Control concurrency with semaphores
- Respect rate limits automatically

**Implementation**:
```python
import asyncio
from xai_sdk import AsyncClient
from xai_sdk.chat import user

async def main():
    client = AsyncClient(
        api_key=os.getenv("XAI_API_KEY"),
        timeout=3600,
    )
    
    requests = [
        "Tell me a joke",
        "Write a funny haiku",
        "Generate a funny X post",
    ]
    
    # Limit concurrent requests (respect rate limits)
    max_concurrent = 2
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process_request(request):
        async with semaphore:
            chat = client.chat.create(model="grok-4", max_tokens=100)
            chat.append(user(request))
            return await chat.sample()
    
    # Process all requests concurrently
    tasks = [process_request(req) for req in requests]
    responses = await asyncio.gather(*tasks)
    
    for response in responses:
        print(response.content)

asyncio.run(main())
```

**Best Practices**:
1. **Respect rate limits**: Set `max_concurrent` based on API rate limits
2. **Use semaphores**: Control maximum in-flight requests
3. **Handle errors**: Wrap in try/except for individual request failures
4. **Monitor usage**: Track token usage across concurrent requests
5. **Timeout handling**: Set appropriate timeouts for reasoning models

**Rate Limit Management**:
- Check rate limits at: https://console.x.ai
- Set `max_concurrent` below your rate limit
- Use semaphores to prevent exceeding limits
- Monitor for rate limit errors (429 responses)

**Benefits**:
- **Faster processing**: Parallel requests vs sequential
- **Better throughput**: Process more requests in same time
- **Efficient resource use**: Better utilization of API capacity
- **Scalable**: Handle hundreds/thousands of requests

**Use Cases**:
1. **Batch processing**: Process multiple documents/queries
2. **Parallel analysis**: Analyze multiple items simultaneously
3. **High-throughput systems**: Handle many concurrent users
4. **Data processing**: Process large datasets efficiently

**Limitations**:
- **No batch API**: X.AI doesn't offer native batch endpoint
- **Rate limits**: Must respect API rate limits
- **Error handling**: Need robust error handling for failures
- **Resource usage**: Higher concurrent requests = more resources

---

## References

- X.AI Grok Voice Agent API: https://docs.x.ai/docs/guides/voice
- X.AI Agentic Tool Calling: https://docs.x.ai/docs/guides/agentic-tool-calling
- X.AI Advanced Usage: https://docs.x.ai/docs/guides/advanced-usage
- X.AI Python SDK: https://github.com/xai-org/xai-python
- Search Tools: https://docs.x.ai/docs/guides/search-tools
- Collections Search: https://docs.x.ai/docs/guides/collections-search
- Code Execution: https://docs.x.ai/docs/guides/code-execution
- Remote MCP Tools: https://docs.x.ai/docs/guides/remote-mcp-tools
