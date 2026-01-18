# ⚠️ Vercel Document Upload Issue - Fix Needed

## The Problem

**Document upload doesn't work on Vercel because:**

1. **Synchronous processing** - Documents are processed synchronously in the request handler
2. **Vercel timeout** - Vercel serverless functions timeout after 60 seconds (max)
3. **Large files** - Document processing (text extraction + embeddings) can take > 60 seconds
4. **ChromaDB embedding** - Generating embeddings is CPU-intensive and slow

---

## Current Implementation

**Code in `backend/app/main.py` (lines 740-760):**

```python
# Process document (in production, this should be async/background job)
try:
    from .rag import process_document
    chunk_count = await process_document(...)  # ❌ This blocks the request
    doc.status = DocumentStatus.COMPLETED
except Exception as e:
    doc.status = DocumentStatus.FAILED
```

**Issue:** This processes the document **synchronously** during the request, which can timeout on Vercel.

---

## Solutions

### Option 1: Make Processing Async (Recommended)

**Queue the document for background processing:**

```python
@app.post("/api/documents", response_model=DocumentResponse)
async def upload_document(...):
    # ... validation ...
    
    # Create document record
    doc = Document(
        client_id=client.id,
        filename=file.filename,
        file_type=allowed_types[file.content_type],
        file_size=file_size,
        status=DocumentStatus.PENDING  # ✅ Start as PENDING
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    
    # Queue for background processing (don't wait)
    # Background job processes document and updates status
    # Client can check status later via GET /api/documents
    
    return doc  # ✅ Return immediately
```

**Then use:**
- Background job queue (Celery, Redis Queue, etc.)
- Or Vercel Cron Jobs
- Or separate processing service

---

### Option 2: Increase Vercel Timeout (Not Recommended)

**Vercel Pro allows up to 300 seconds**, but still not ideal for large documents.

**Also requires:**
- Pro plan ($20/month per team)
- Still not ideal for production

---

### Option 3: Move to Railway/Render (Best for Production)

**Backend is already on Railway:**
- ✅ No function timeout limits
- ✅ Can process documents synchronously
- ✅ Better for file uploads

**Keep Vercel for:**
- Frontend/dashboard
- Static files

**Use Railway for:**
- Backend API (already deployed)
- Document processing

---

## Recommended Fix

### Quick Fix: Make Processing Async

**Update `/api/documents` endpoint:**

1. **Save file to storage** (Vercel Blob, S3, or Railway)
2. **Return document with PENDING status** (immediate response)
3. **Process in background** (separate worker or cron job)

### Production Fix: Use Railway

**The backend is already on Railway** (`snip-production.up.railway.app`):

- ✅ No timeout limits
- ✅ Can process documents synchronously
- ✅ Better for file uploads
- ✅ Already working

**Solution:** Make sure document uploads go to Railway, not Vercel.

---

## Immediate Action

**Check where document uploads are going:**

1. **If backend is on Railway** → Document upload should work
2. **If backend is on Vercel** → Move to Railway or make async

**Backend URL:** `https://snip-production.up.railway.app` ✅

**This is Railway, not Vercel!** So document upload should work.

---

## Possible Issues

### Issue 1: Frontend Sending to Wrong URL

**Check frontend is using Railway backend:**

```typescript
// Should be:
const apiUrl = 'https://snip-production.up.railway.app'

// Not:
const apiUrl = 'https://backend.vercel.app'
```

### Issue 2: Processing Timeout

**Even on Railway, large documents might timeout.**

**Fix:** Make processing async (start PENDING, update status later).

---

## Summary

**If document upload doesn't work on Vercel:**

1. ✅ **Backend is on Railway** - Should work (no timeout limits)
2. ⚠️ **Make processing async** - Don't process during request
3. ✅ **Return PENDING status** - Process in background

**Next step:** Check where the upload is actually going (Railway vs Vercel).
