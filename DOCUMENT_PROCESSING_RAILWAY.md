# Document Processing on Railway

## Why documents stayed "Pending"

Uploaded documents were queued with **FastAPI BackgroundTasks** (run *after* the HTTP response is sent). On Railway (and many PaaS), the request lifecycle often ends when the response is delivered, so **background tasks may never run**. That left documents stuck in **PENDING**.

## Fix (in code)

- **Document processing now runs in-request** in `POST /api/documents`: we create the record, set status to PROCESSING, call `process_document()` (extract text → chunk → ChromaDB), then set COMPLETED or FAILED and return. The response is sent only after processing finishes.
- **ChromaDB persist directory** is created explicitly in `process_document()` so Railway’s filesystem has a writable path.

## What you need to do

1. **Deploy the backend** to Railway (push to `main` or trigger deploy so the new code is live).
2. **Existing PENDING documents** will not be processed by the old background task. For those two docs:
   - **Re-upload the same files** from the dashboard (Documents). The new upload will process in-request and show **Completed** (or Failed with an error message).
   - Optionally delete the old PENDING rows from the dashboard if your UI supports it, to avoid confusion.
3. **Railway logs**: In Railway → your service → **Logs**, filter or search for `[Documents]`. You should see, in order:
   - `[Documents] Created doc id=... filename=... size=...`
   - `[Documents] Processing doc id=... ...`
   - Then either:
     - `[Documents] Processed doc id=... filename=... chunks=N` (success), or  
     - `[Documents] Failed doc id=... filename=...: <error>` plus a Python traceback (failure).
   If you see "Created" but never "Processing", the failure is before RAG (e.g. DB). If you see "Processing" then "Failed", the traceback shows the cause (e.g. ChromaDB, extract text, or timeout).

## RAG usage (how the bot uses your documents)

Yes — the bot **does** process and use this information. The flow is:

1. **Upload** → Text is extracted from the file, split into chunks (with overlap), and stored in **ChromaDB** in a per-client collection `client_<client_id>`. ChromaDB generates embeddings for each chunk (same model for add and query).
2. **Every chat** (Standard+ tier only) → Before calling the AI, the backend runs `retrieve_context(client.id, request.message)`: it embeds the user’s message, does a **similarity search** in that client’s collection, and returns the top 5 most relevant chunks (distance &lt; 1.5).
3. **Prompt** → Those chunks are injected into the system prompt as:
   ```
   RELEVANT CONTEXT FROM COMPANY DOCUMENTS:
   [From: yourfile.pdf]
   <chunk 1>
   ---
   [From: yourfile.pdf]
   <chunk 2>
   ...
   Use this context to answer questions when relevant.
   ```
4. The model (Grok) sees the user message **and** this context, and is instructed to use it when relevant. So answers are grounded in your uploaded docs.

**Tiers:** Only **Standard** and **Premium** clients get RAG; **Basic** tier does not (document upload is disabled for Basic). Same `client_id` is used for both storing chunks (upload) and retrieving (chat), so each client only sees their own documents.

## Optional: ChromaDB on Railway

- Default persist path is `./chroma_data`. On Railway the filesystem is **ephemeral** (data is lost on redeploy). For persistent document embeddings across deploys, you’d need a **volume** or external store (e.g. configure ChromaDB to use a persistent path via `CHROMA_PERSIST_DIRECTORY` and attach a Railway volume to that path). For now, re-uploading after a deploy is the workaround if you need documents to persist.
