# Environment Variables & Settings Verification Report

**Date:** 2026-01-16  
**Status:** ⚠️ **VERIFICATION IN PROGRESS**

---

## Required Environment Variables for TTS

### Backend (Railway) - Required Variables

#### 1. **DATABASE_URL** (Required - Provided by Railway)
- **Purpose:** PostgreSQL database connection string
- **Format:** `postgresql://user:password@host:port/database`
- **Railway Status:** ✅ Automatically provided by Railway Postgres service
- **Verification:** Railway links Postgres service automatically
- **Action:** ✅ No action needed (Railway handles this)

#### 2. **XAI_API_KEY** (Required for TTS)
- **Purpose:** xAI API key for Grok chat completions and TTS voice generation
- **Format:** `xai-xxxxxxxxxxxxxxxxxxxxx`
- **Required For:** 
  - Chat completions (Grok AI responses)
  - TTS voice generation (xAI Grok Voice Agent API)
- **Where Used:** `backend/app/main.py` - lines 494-534, 657-671
- **Fallback Order:**
  1. Client's `config.ai_api_key` (if set via dashboard)
  2. Legacy `config.xai_api_key` (if present)
  3. `settings.xai_api_key` from environment variable
- **Railway Status:** ⚠️ **NEEDS VERIFICATION**
- **Action:** Verify `XAI_API_KEY` is set in Railway environment variables

#### 3. **XAI_TTS_VOICE** (Optional - New Feature)
- **Purpose:** Select voice for TTS (default: 'Ara')
- **Format:** One of: `Ara`, `Leo`, `Rex`, `Sal`, `Eve`
- **Default:** `'Ara'` (if not set)
- **Where Used:** `backend/app/main.py` - line 663
- **Code:** `voice = getattr(config, 'tts_voice', None) or os.getenv('XAI_TTS_VOICE', 'Ara')`
- **Railway Status:** ⚠️ **OPTIONAL** - Can be set later if desired
- **Action:** Optional - Only set if you want a different voice than 'Ara'

### Backend (Railway) - Optional Variables

#### 4. **WIDGET_CDN_URL** (Optional - Has Default)
- **Purpose:** URL where widget.js is hosted
- **Default:** `https://widget-sigma-sage.vercel.app`
- **Current Value:** ✅ `https://widget-sigma-sage.vercel.app` (from `config.py`)
- **Where Used:** `backend/app/main.py` - line 715, 727
- **Railway Status:** ✅ Has default value
- **Action:** ✅ No action needed (default is correct)

---

## Configuration Settings Check

### Backend Configuration (`backend/app/config.py`)

✅ **Database URL:**
- Config: `database_url: str = "postgresql://localhost:5432/snip"` (default)
- Railway: Automatically uses `DATABASE_URL` from environment
- Status: ✅ Correct (Railway overrides default)

✅ **Widget CDN URL:**
- Config: `widget_cdn_url: str = "https://widget-sigma-sage.vercel.app"`
- Status: ✅ Correct (matches production widget URL)

✅ **CORS Settings:**
- Config: `cors_origins: list[str] = ["*"]`
- Status: ✅ Correct (allows widget from any domain)

### TTS Configuration (`backend/app/main.py`)

✅ **xAI TTS Endpoints:**
- WebSocket: `wss://api.x.ai/v1/realtime` ✅
- Ephemeral Token: `https://api.x.ai/v1/realtime/client_secrets` ✅
- Status: ✅ Correct

✅ **Retry Logic:**
- Retries: `3` attempts ✅
- Backoff: Exponential (0.5s, 1.0s, 1.5s) ✅
- Status: ✅ Correct

✅ **Voice Configuration:**
- Default Voice: `'Ara'` ✅
- Valid Voices: `['Ara', 'Leo', 'Rex', 'Sal', 'Eve']` ✅
- Validation: ✅ Present (line 664-665)
- Status: ✅ Correct

---

## Widget Configuration Check

### Widget Settings (`widget/src/widget.ts`)

✅ **API URL Detection:**
- From: `data-api-url` attribute or script origin
- Status: ✅ Correct (lines 691-692)

✅ **Client ID:**
- From: `data-client-id` attribute
- Status: ✅ Correct (line 688)

✅ **TTS Error Recovery:**
- Fallback: Browser TTS on audio URL failure ✅
- Status: ✅ Correct

---

## Verification Checklist

### Required Actions:

- [ ] **Verify `XAI_API_KEY` is set in Railway**
  - Go to Railway Dashboard → Snip service → Variables
  - Check if `XAI_API_KEY` exists and has a valid value
  - If missing: Add `XAI_API_KEY` with your xAI API key

- [ ] **Verify `DATABASE_URL` is set (Railway auto-provisions)**
  - Railway automatically sets this when Postgres service is linked
  - Should be visible in Variables tab
  - Format: `postgresql://...` or `postgres://...` (both work)

### Optional Actions:

- [ ] **Set `XAI_TTS_VOICE` if you want a different voice**
  - Only needed if you want to change from default 'Ara'
  - Options: `Ara`, `Leo`, `Rex`, `Sal`, `Eve`
  - Can be set later without affecting functionality

---

## How to Verify Railway Variables

### Option 1: Railway Dashboard (Recommended)
1. Go to: https://railway.app/project/02602f57-7c35-468a-abb3-678af0f43fe1
2. Click on "Snip" service
3. Go to "Variables" tab
4. Check for:
   - ✅ `DATABASE_URL` (should be present from Postgres)
   - ⚠️ `XAI_API_KEY` (verify it's set)
   - ⏳ `XAI_TTS_VOICE` (optional)

### Option 2: Railway CLI
```bash
cd backend
railway service  # Link service if needed
railway variables  # List all variables
railway variables get XAI_API_KEY  # Get specific variable
```

---

## Expected Variables in Railway

### Required:
```
DATABASE_URL=postgresql://postgres:password@postgres.railway.internal:5432/railway
XAI_API_KEY=xai-xxxxxxxxxxxxxxxxxxxxx
```

### Optional:
```
XAI_TTS_VOICE=Ara  # or Leo, Rex, Sal, Eve
```

---

## Troubleshooting

### If `XAI_API_KEY` is missing:
1. Get your xAI API key from https://console.x.ai
2. Go to Railway Dashboard → Snip service → Variables
3. Click "New Variable"
4. Name: `XAI_API_KEY`
5. Value: `xai-xxxxxxxxxxxxxxxxxxxxx`
6. Click "Add"
7. Redeploy service (or wait for auto-redeploy)

### If `DATABASE_URL` is missing:
1. Check Postgres service is linked in Railway
2. Railway should automatically set `DATABASE_URL`
3. If missing: Link Postgres service in Railway dashboard

### If TTS is not working:
1. Verify `XAI_API_KEY` is set correctly
2. Check backend logs for `[TTS]` messages
3. Verify client's `ai_provider` is set to `'xai'`
4. Check client's `ai_api_key` is set (if using BYOK)

---

## Code Reference

### Where Environment Variables Are Used:

**`XAI_API_KEY`:**
- `backend/app/config.py` - line 21 (settings)
- `backend/app/main.py` - line 534 (fallback to settings)
- `backend/app/main.py` - line 657 (TTS generation check)

**`XAI_TTS_VOICE`:**
- `backend/app/main.py` - line 663 (voice selection)
- `os.getenv('XAI_TTS_VOICE', 'Ara')` - falls back to 'Ara'

**`DATABASE_URL`:**
- `backend/app/config.py` - line 14 (case_sensitive=False allows Railway's format)
- `backend/app/database.py` - used for SQLAlchemy connection
- Railway provides this automatically

**`WIDGET_CDN_URL`:**
- `backend/app/config.py` - line 35 (default value)
- `backend/app/main.py` - lines 715, 727 (embed snippet generation)
- Can be overridden via environment variable

---

## Summary

### ✅ Confirmed Correct:
- Database URL (Railway auto-provisions) ✅
- Widget CDN URL (default correct) ✅
- TTS endpoint URLs ✅
- Retry logic configuration ✅
- Voice validation ✅
- Widget API URL detection ✅

### ⚠️ Needs Verification:
- `XAI_API_KEY` in Railway (required for TTS)
- `DATABASE_URL` in Railway (should be auto-provided)

### ⏳ Optional:
- `XAI_TTS_VOICE` (optional, defaults to 'Ara')

---

**Next Steps:** Verify `XAI_API_KEY` is set in Railway Dashboard!

---

**Last Updated:** 2026-01-16  
**Prepared By:** TTSSnippetMaster
