# Deployment Needed for TTS Fixes

**Date:** 2026-01-16  
**Status:** ✅ **Changes Ready - Need to Deploy**

---

## Yes - You Need to Update Railway (and Vercel for Widget)

### Summary

**Two deployments needed:**
1. **Railway (Backend)** - Deploy TTS fixes to backend (`backend/app/main.py`)
2. **Vercel (Widget)** - Deploy TTS fixes to widget (`widget/src/widget.ts`)

---

## Changes Made

### Backend Changes (`backend/app/main.py`)
✅ **Retry Logic for Ephemeral Token**
- Added retry logic with exponential backoff (3 attempts)
- Better error handling (no retry on auth errors)
- Improved reliability for TTS generation

✅ **Voice Configuration**
- Added support for `XAI_TTS_VOICE` environment variable
- Voice validation (Ara, Leo, Rex, Sal, Eve)
- Fallback to 'Ara' if invalid

### Widget Changes (`widget/src/widget.ts`)
✅ **Memory Leak Fix**
- Added `currentAudio` property to track audio elements
- Proper cleanup on error/end events

✅ **Race Condition Fix**
- Added `isPlayingAudio` flag
- Prevent multiple simultaneous audio playback

✅ **Error Recovery**
- Automatic fallback to browser TTS on failures
- Enhanced error handling

✅ **Accessibility**
- ARIA live regions for screen readers
- WCAG 2.1 AA compliant

✅ **Long Text Handling**
- Automatic chunking for browser TTS
- Sentence-based splitting

---

## Deployment Steps

### Step 1: Commit Changes

```bash
cd /Users/nexteleven/snip/Snip

# Add backend changes
git add backend/app/main.py

# Add widget changes
git add widget/src/widget.ts

# Commit with descriptive message
git commit -m "Fix TTS implementation: Add retry logic, memory leak fixes, error recovery, and accessibility features"
```

### Step 2: Deploy Backend to Railway

**Option A: Auto-Deploy (if enabled)**
- Just push to GitHub: `git push origin main`
- Railway will automatically deploy if auto-deploy is enabled

**Option B: Manual Deploy via Railway Dashboard**
1. Go to: https://railway.app/project/02602f57-7c35-468a-abb3-678af0f43fe1
2. Click on "Snip" service
3. Go to "Deployments" tab
4. Click "Redeploy" or "Deploy Latest"

**Option C: Railway CLI**
```bash
cd backend
railway up
```

### Step 3: Build and Deploy Widget to Vercel

**Option A: Auto-Deploy (if enabled)**
- Just push to GitHub: `git push origin main`
- Vercel will automatically build and deploy if connected

**Option B: Manual Build and Deploy**
```bash
cd widget

# Build the widget
npm run build

# Deploy to Vercel (if CLI is set up)
vercel --prod
```

**Option C: Vercel Dashboard**
1. Go to Vercel dashboard
2. Select widget project
3. Click "Redeploy" or trigger new deployment

---

## What Gets Deployed

### Backend (Railway)
- ✅ Retry logic for ephemeral token (3 attempts with exponential backoff)
- ✅ Voice configuration via `XAI_TTS_VOICE` environment variable
- ✅ Better error handling for TTS generation

### Widget (Vercel)
- ✅ Memory leak fixes (audio element cleanup)
- ✅ Race condition fixes (single audio playback)
- ✅ Error recovery (automatic browser TTS fallback)
- ✅ Accessibility features (ARIA live regions)
- ✅ Long text handling (automatic chunking)

---

## Optional: Environment Variable

If you want to change the default voice, set in Railway:

**Railway Environment Variable:**
- **Key:** `XAI_TTS_VOICE`
- **Value:** One of: `Ara`, `Leo`, `Rex`, `Sal`, `Eve`
- **Default:** `Ara` (if not set)

**To Set:**
1. Go to Railway dashboard
2. Click on "Snip" service
3. Go to "Variables" tab
4. Add `XAI_TTS_VOICE` = `Ara` (or desired voice)
5. Redeploy service

---

## Verification After Deployment

### Backend Verification
```bash
# Test TTS generation (requires XAI_API_KEY)
cd backend
python -m test_xai_tts
```

### Widget Verification
1. Visit your website with the widget
2. Send a test message
3. Verify audio plays automatically
4. Check browser console for `[TTS]` logs
5. Test error recovery (disable network, should fallback)

---

## Important Notes

### Railway Auto-Deploy
- ⚠️ If auto-deploy is enabled, changes will deploy automatically on `git push`
- ✅ Recommended: Enable auto-deploy for seamless updates
- ⚠️ If disabled, manually redeploy after pushing

### Widget CDN URL
- The widget CDN URL (`https://widget-sigma-sage.vercel.app`) will update automatically
- No changes needed to embed code on websites
- Widget will use new version after Vercel deployment completes

### Backward Compatibility
- ✅ All changes are backward compatible
- ✅ Default behavior unchanged (voice still works)
- ✅ Enhancements are additive (retry, fallback, etc.)

---

## Rollback Plan

If something goes wrong:

**Railway:**
1. Go to Railway dashboard
2. Deployments tab
3. Select previous successful deployment
4. Click "Redeploy"

**Vercel:**
1. Go to Vercel dashboard
2. Deployments tab
3. Select previous successful deployment
4. Click "Promote to Production"

---

## Status

- ✅ **Changes Ready:** Code changes complete
- ⏳ **Needs Commit:** Changes not yet committed
- ⏳ **Needs Push:** Changes not yet pushed to GitHub
- ⏳ **Needs Deploy:** Railway and Vercel need deployment

**Next Step:** Commit, push, and deploy!

---

**Last Updated:** 2026-01-16  
**Prepared By:** TTSSnippetMaster
