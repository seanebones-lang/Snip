# Grok Code Fast 1 - Prompt Engineering Guide

## Overview

`grok-code-fast-1` is a lightweight agentic model designed to excel as a pair-programmer inside most common coding tools. It's optimized for agentic coding tasks with tool calling, delivering up to 4x the speed and 1/10th the cost of other leading agentic models.

## Key Characteristics

- **Agentic coding model**: Designed for tool-call-heavy domains
- **Fast and affordable**: 4x speed, 1/10th cost of other agentic models
- **Reasoning model**: Interleaved tool-calling during thinking
- **Native tool calling**: First-party support for tool calling
- **Streaming reasoning**: Thinking traces via `chunk.choices[0].delta.reasoning_content`

## Best Practices

### 1. Provide Necessary Context

**Avoid**: Vague, no-context prompts
```
❌ Make error handling better
```

**Good**: Specific context with file references
```
✅ My error codes are defined in @errors.ts, can you use that as reference 
   to add proper error handling and error codes to @sql.ts where I am 
   making queries
```

**Tips**:
- Specify relevant file paths
- Reference project structures
- Include dependencies
- Avoid irrelevant context
- Use file references (`@filename`) when available

### 2. Set Explicit Goals and Requirements

**Avoid**: Vague, underspecified prompts
```
❌ Create a food tracker
```

**Good**: Detailed, concrete requirements
```
✅ Create a food tracker which shows the breakdown of calorie consumption 
   per day divided by different nutrients when I enter a food item. Make 
   it such that I can see an overview as well as get high level trends.
```

**Tips**:
- Clearly define goals
- Specify the problem to solve
- Include requirements and constraints
- Be concrete and detailed

### 3. Continually Refine Your Prompts

Take advantage of the fast iteration speed to refine prompts:

**Example Refinement**:
```
The previous approach didn't consider the IO heavy process which can block 
the main thread, we might want to run it in its own threadloop such that 
it does not block the event loop instead of just using the async lib version
```

**Tips**:
- Iterate quickly (4x speed advantage)
- Reference specific failures from first attempt
- Add more context based on results
- Refine based on output quality

### 4. Assign Agentic Tasks

**Model Selection Guide**:

| Task Type | Recommended Model | Why |
|-----------|------------------|-----|
| Agentic coding tasks | `grok-code-fast-1` | Fast, tool-call optimized, cost-effective |
| One-shot Q&A | Grok 4 models | Better for complex concepts, deep analysis |
| Large codebase navigation | `grok-code-fast-1` | Designed for tool-heavy exploration |
| Complex debugging (with context) | Grok 4 | Better reasoning with full context |

**Think of it this way**:
- **`grok-code-fast-1`**: Works quickly and tirelessly to find answers or implement changes
- **Grok 4**: Best for diving deep into complex concepts when you provide all context upfront

### 5. Use Native Tool Calling

**Best Practice**:
- ✅ Use native tool calling (first-party support)
- ❌ Avoid XML-based tool-call outputs (may hurt performance)

**Example**:
```python
from xai_sdk.tools import code_execution

chat = client.chat.create(
    model="grok-code-fast-1",
    tools=[code_execution()],  # Native tool calling
)
```

### 6. Give Detailed System Prompts

**Best Practice**:
- Be thorough in system prompt
- Describe the task clearly
- Set expectations
- List edge cases
- Define constraints

**Example**:
```
You are a senior Python developer. Your task is to refactor this codebase 
to improve error handling. 

Requirements:
- Use error codes from errors.ts
- Handle all database query errors
- Log errors appropriately
- Return user-friendly error messages

Edge cases to consider:
- Network timeouts
- Database connection failures
- Invalid input data
- Concurrent access issues
```

### 7. Introduce Context Effectively

**Best Practice**:
- Use XML tags or Markdown formatting
- Mark various sections clearly
- Use descriptive headings/tags
- Define sections explicitly

**Example**:
```markdown
## Project Structure
- `/src/api/` - API endpoints
- `/src/db/` - Database layer
- `/src/utils/` - Utility functions

## Current Issue
The error handling in @sql.ts doesn't use the error codes from @errors.ts.

## Requirements
- Add proper error handling
- Use error codes from @errors.ts
- Log errors with context
```

### 8. Optimize for Cache Hits

**Best Practice**:
- Keep prompt history consistent
- Avoid changing/augmenting prompt history
- Let cache work for repeated prefixes
- Cache hits significantly speed up inference

**Why It Matters**:
- In agentic tasks, most of the prefix remains the same
- Cache automatically retrieves repeated content
- Changing prompt history leads to cache misses
- Cache misses = significantly slower inference

## For API Developers

### Reasoning Content

`grok-code-fast-1` is a reasoning model with thinking traces:

```python
# Streaming mode required for reasoning content
for response, chunk in chat.stream():
    if chunk.choices[0].delta.reasoning_content:
        print(chunk.choices[0].delta.reasoning_content)
```

**Note**: Thinking traces only accessible in streaming mode.

### Tool Calling

Designed for native tool calling with interleaved thinking:

```python
from xai_sdk.tools import code_execution

chat = client.chat.create(
    model="grok-code-fast-1",
    tools=[code_execution()],
    include=["verbose_streaming"],
)

chat.append(user("Refactor this code to use async/await properly"))
```

### Performance Characteristics

- **Speed**: Up to 4x faster than other agentic models
- **Cost**: 1/10th the cost of other agentic models
- **Tool calls**: Optimized for multiple sequential tool calls
- **Cache**: Benefits significantly from cache hits

## Use Cases

### Ideal For
- ✅ Agentic coding tasks
- ✅ Large codebase navigation
- ✅ Tool-call-heavy domains
- ✅ Rapid iteration and refinement
- ✅ Code refactoring with tools
- ✅ Finding answers across codebase

### Not Ideal For
- ❌ One-shot Q&A (use Grok 4 instead)
- ❌ Complex debugging with full context (use Grok 4)
- ❌ Deep conceptual analysis (use Grok 4)

## Example Workflow

```python
from xai_sdk import Client
from xai_sdk.chat import user, system
from xai_sdk.tools import code_execution

client = Client(api_key=os.getenv("XAI_API_KEY"))

# Step 1: Detailed system prompt
system_prompt = """
You are a senior Python developer. Refactor the code in @sql.ts to:
1. Use error codes from @errors.ts
2. Add proper error handling for all database queries
3. Log errors with context
4. Return user-friendly error messages

Edge cases: network timeouts, connection failures, invalid input.
"""

# Step 2: Provide context
user_prompt = """
The error codes are defined in @errors.ts:
- DB_CONNECTION_ERROR: "Database connection failed"
- QUERY_TIMEOUT: "Query execution timeout"
- INVALID_INPUT: "Invalid input parameters"

Current code in @sql.ts makes queries without proper error handling.
Please add error handling using the codes from @errors.ts.
"""

# Step 3: Use grok-code-fast-1 with tools
chat = client.chat.create(
    model="grok-code-fast-1",
    tools=[code_execution()],
    include=["verbose_streaming"],
)

chat.append(system(system_prompt))
chat.append(user(user_prompt))

# Step 4: Stream and see reasoning
for response, chunk in chat.stream():
    # View tool calls
    for tool_call in chunk.tool_calls:
        print(f"Tool: {tool_call.function.name}")
    
    # View reasoning (if available)
    if chunk.choices[0].delta.reasoning_content:
        print(f"Thinking: {chunk.choices[0].delta.reasoning_content}")
    
    # View content
    if chunk.content:
        print(chunk.content, end="", flush=True)

# Step 5: Refine if needed
if not satisfied_with_result:
    chat.append(user("The previous approach didn't handle concurrent access. Add proper locking."))
    # Iterate quickly...
```

## Summary

**Key Takeaways**:
1. **Be specific**: Provide context, file paths, requirements
2. **Be detailed**: Explicit goals and requirements
3. **Iterate quickly**: Take advantage of 4x speed
4. **Use for agentic tasks**: Tool-call-heavy coding work
5. **Use native tools**: First-party tool calling support
6. **Optimize cache**: Keep prompt history consistent
7. **Stream for reasoning**: Access thinking traces via streaming

**Model Selection**:
- **`grok-code-fast-1`**: Agentic coding, tool-heavy tasks, fast iteration
- **Grok 4**: One-shot Q&A, complex debugging, deep analysis

## References

- Function Calling Guide: https://docs.x.ai/docs/guides/function-calling
- Model Information: https://docs.x.ai/docs/models
- API Reference: https://docs.x.ai/docs/api-reference
