# Deployment Execution Guide - Railway & Vercel

**Date**: 2026-01-16  
**Status**: ✅ **READY FOR DEPLOYMENT**

---

## 🎯 Overview

This guide provides step-by-step instructions to:
1. ✅ Execute database migration on Railway
2. ✅ Deploy backend changes to Railway
3. ✅ Deploy widget changes to Vercel
4. ✅ Deploy dashboard changes to Vercel
5. ✅ Verify all deployments

---

## ✅ Pre-Deployment Checklist

### Code Status ✅
- [x] All code committed (11 commits)
- [x] All code pushed to repository
- [x] Database migration script created
- [x] Auto-migration added to `database.py`
- [x] All configurations verified

### Migration Status ⚠️
- [x] Migration SQL script created: `backend/migrations/add_customization_columns.sql`
- [x] Migration Python script created: `backend/run_customization_migration.py`
- [x] Auto-migration added to `backend/app/database.py` (runs on startup)

---

## 🚀 Step 1: Database Migration on Railway

### Option A: Automatic Migration (Recommended) ✅

**The migration will run automatically** when Railway deploys the new code because:
- `init_db()` is called on startup (`main.py` line 293)
- `init_db()` includes the customization migration (`database.py` lines 56-67)

**No manual action required** - just deploy the code and the migration runs automatically on startup.

### Option B: Manual Migration (If Needed)

If you want to run migration manually before deployment:

**Via Railway CLI**:
```bash
# Connect to Railway database
railway connect

# Run SQL migration
psql $DATABASE_URL < backend/migrations/add_customization_columns.sql

# Or run Python script
railway run python backend/run_customization_migration.py
```

**Via Railway Dashboard**:
1. Go to Railway dashboard
2. Select your PostgreSQL service
3. Click "Query" tab
4. Copy/paste SQL from `backend/migrations/add_customization_columns.sql`
5. Execute

**Verify Migration**:
```sql
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'client_configs'
AND column_name IN ('widget_width', 'widget_height', 'custom_css', 'theme')
ORDER BY column_name;
```

**Expected**: 4 rows returned

---

## 🚂 Step 2: Deploy Backend to Railway

### Automatic Deployment ✅

**Railway will auto-deploy** when you push to the repository (if configured).

**To trigger deployment**:
```bash
# Code is already pushed, but verify:
git push

# Railway will automatically:
# 1. Build the application
# 2. Install dependencies from requirements.txt
# 3. Run startup script (which calls init_db() - migration runs automatically)
# 4. Start the application
```

### Manual Deployment (If Needed)

**Via Railway CLI**:
```bash
# Link to project
railway link --project YOUR_PROJECT_ID

# Deploy
railway up
```

**Via Railway Dashboard**:
1. Go to Railway dashboard
2. Select your backend service
3. Click "Deploy" (if not auto-deploy)
4. Or wait for auto-deploy from git push

### Verify Backend Deployment ✅

```bash
# Health check
curl https://snip-production.up.railway.app/healthz

# Expected: {"status":"ok","service":"snip"}

# Check migration in logs
# Railway Dashboard → Service → Deployments → Logs
# Look for: "✅ Migration check: Customization columns verified/added"
```

### Backend Configuration ✅

**Files Verified**:
- ✅ `railway.json` - Correct start command
- ✅ `nixpacks.toml` - Correct build configuration
- ✅ `Procfile` - Correct process command
- ✅ `requirements.txt` - All dependencies included
- ✅ `backend/app/database.py` - Auto-migration enabled

**Environment Variables** (Railway should already have):
- `DATABASE_URL` - PostgreSQL connection string
- `XAI_API_KEY` - xAI API key
- `CHROMA_PERSIST_DIRECTORY` - ChromaDB directory

---

## 📦 Step 3: Deploy Widget to Vercel

### Automatic Deployment ✅

**Vercel will auto-deploy** when you push to the repository (if configured).

**To trigger deployment**:
```bash
# Code is already pushed
# Vercel will automatically:
# 1. Build widget (npm run build)
# 2. Deploy to widget-sigma-sage.vercel.app
# 3. Serve widget.js with CORS headers
```

### Manual Deployment (If Needed)

**Via Vercel CLI**:
```bash
cd widget
npm install
npm run build

# Deploy (if CLI installed)
vercel --prod
```

**Via Vercel Dashboard**:
1. Go to Vercel dashboard
2. Select widget project
3. Click "Deploy" or trigger from git push

### Verify Widget Deployment ✅

```bash
# Check widget.js exists
curl -I https://widget-sigma-sage.vercel.app/widget.js

# Expected: 200 OK with CORS headers

# Check CORS headers
curl -H "Origin: https://example.com" -I https://widget-sigma-sage.vercel.app/widget.js

# Expected: Access-Control-Allow-Origin: *
```

### Widget Configuration ✅

**Files Verified**:
- ✅ `widget/vercel.json` - CORS headers configured
- ✅ `widget/vite.config.ts` - Build configuration correct
- ✅ `widget/package.json` - Dependencies correct

---

## 🎨 Step 4: Deploy Dashboard to Vercel

### Automatic Deployment ✅

**Vercel will auto-deploy** when you push to the repository (if configured).

**To trigger deployment**:
```bash
# Code is already pushed
# Vercel will automatically:
# 1. Build dashboard (npm run build)
# 2. Deploy to snip.mothership-ai.com (or configured domain)
# 3. Configure API rewrites
```

### Manual Deployment (If Needed)

**Via Vercel CLI**:
```bash
cd dashboard
npm install
npm run build

# Deploy (if CLI installed)
vercel --prod
```

**Via Vercel Dashboard**:
1. Go to Vercel dashboard
2. Select dashboard project
3. Click "Deploy" or trigger from git push

### Verify Dashboard Deployment ✅

```bash
# Check dashboard loads
curl -I https://snip.mothership-ai.com

# Expected: 200 OK

# Test API proxy
curl https://snip.mothership-ai.com/api/healthz

# Expected: {"status":"ok","service":"snip"}
```

### Dashboard Configuration ✅

**Files Verified**:
- ✅ `dashboard/vercel.json` - API rewrites configured
- ✅ `dashboard/package.json` - Dependencies correct

**Environment Variables** (Vercel should already have):
- `VITE_API_URL` - Backend API URL (https://snip-production.up.railway.app)

---

## ✅ Step 5: Post-Deployment Verification

### 1. Database Migration Verification ✅

**Check Migration Status**:

```bash
# Option A: Check Railway logs
# Railway Dashboard → Service → Deployments → Latest → Logs
# Look for: "✅ Migration check: Customization columns verified/added"

# Option B: Run verification SQL
railway connect
psql $DATABASE_URL -c "SELECT column_name FROM information_schema.columns WHERE table_name = 'client_configs' AND column_name IN ('widget_width', 'widget_height', 'custom_css', 'theme');"

# Expected: 4 rows (widget_width, widget_height, custom_css, theme)
```

### 2. Backend Verification ✅

**Test Endpoints**:

```bash
# Health check
curl https://snip-production.up.railway.app/healthz
# Expected: {"status":"ok","service":"snip"}

# Widget config (should include new fields)
curl https://snip-production.up.railway.app/api/widget/config/YOUR_CLIENT_ID | jq '.'
# Verify: width, height, customCss, theme fields present

# API docs
curl https://snip-production.up.railway.app/docs
# Expected: 200 OK (Swagger UI loads)
```

### 3. Widget Verification ✅

**Test Widget**:

```bash
# Check widget loads
curl -I https://widget-sigma-sage.vercel.app/widget.js
# Expected: 200 OK

# Check CORS
curl -H "Origin: https://example.com" -I https://widget-sigma-sage.vercel.app/widget.js
# Verify: Access-Control-Allow-Origin: *
```

**Test Widget on Page**:
1. Create test HTML page with widget script
2. Load page in browser
3. Verify widget appears
4. Test customization options (if configured)

### 4. Dashboard Verification ✅

**Test Dashboard**:

```bash
# Check dashboard loads
curl -I https://snip.mothership-ai.com
# Expected: 200 OK

# Test login (manual)
# 1. Open dashboard in browser
# 2. Login with API key
# 3. Navigate to Branding page
# 4. Verify all customization options visible:
#    - Widget width/height inputs
#    - Theme dropdown
#    - Custom CSS textarea
#    - Position dropdown (5 options)
```

### 5. End-to-End Testing ✅

**Test Complete Flow**:

1. **Dashboard → Customization**:
   - Set widget width: 400px
   - Set widget height: 600px
   - Select theme: Light
   - Add custom CSS: `.snip-chat { border-radius: 20px; }`
   - Save

2. **Verify Widget Config API**:
   ```bash
   curl https://snip-production.up.railway.app/api/widget/config/YOUR_CLIENT_ID | jq '.'
   # Verify: width: 400, height: 600, theme: "light", customCss present
   ```

3. **Test Widget on Page**:
   - Widget should reflect all customizations
   - Width should be 400px
   - Height should be 600px
   - Theme should be light
   - Custom CSS should apply

---

## 🔍 Troubleshooting

### Migration Not Running

**Issue**: Migration not executing on Railway startup

**Solution 1**: Check logs for migration errors
```bash
# Railway Dashboard → Service → Deployments → Latest → Logs
# Look for migration messages
```

**Solution 2**: Run migration manually
```bash
railway connect
psql $DATABASE_URL < backend/migrations/add_customization_columns.sql
```

**Solution 3**: Verify init_db() is called
```bash
# Check logs for: "✅ Migration check: Customization columns verified/added"
# If not present, check startup logs
```

### Widget Not Loading

**Issue**: Widget.js not accessible or CORS errors

**Solution**:
1. Check Vercel deployment status
2. Verify `widget/vercel.json` has CORS headers
3. Clear browser cache
4. Check widget URL in script tag matches deployment

### Dashboard Not Working

**Issue**: Dashboard can't connect to backend

**Solution**:
1. Verify `VITE_API_URL` environment variable in Vercel
2. Check `dashboard/vercel.json` has API rewrites
3. Verify backend is accessible: `curl https://snip-production.up.railway.app/healthz`

### Customization Not Working

**Issue**: Widget doesn't reflect customization changes

**Solution**:
1. Verify migration completed (check columns exist)
2. Verify backend returns new fields in widget config
3. Check widget version (clear cache)
4. Verify widget code includes customization support

---

## 📊 Deployment Status Checklist

### Railway (Backend) ✅
- [ ] Migration script created (`backend/migrations/add_customization_columns.sql`)
- [ ] Migration Python script created (`backend/run_customization_migration.py`)
- [ ] Auto-migration enabled (`backend/app/database.py`)
- [ ] Code pushed to repository
- [ ] Railway auto-deploys (or manual deploy)
- [ ] Migration runs on startup (check logs)
- [ ] Health check passes (`/healthz`)
- [ ] Widget config includes new fields

### Vercel (Widget) ✅
- [ ] Code pushed to repository
- [ ] Vercel auto-deploys (or manual deploy)
- [ ] Widget.js accessible (`/widget.js`)
- [ ] CORS headers configured
- [ ] Widget loads on test page
- [ ] Customization options work

### Vercel (Dashboard) ✅
- [ ] Code pushed to repository
- [ ] Vercel auto-deploys (or manual deploy)
- [ ] Dashboard accessible
- [ ] API rewrites working
- [ ] Branding page shows all options
- [ ] Customization saves successfully

---

## ✅ Final Verification

### All Systems Go ✅

Run this comprehensive verification:

```bash
# 1. Backend Health
curl https://snip-production.up.railway.app/healthz
# Expected: {"status":"ok","service":"snip"}

# 2. Widget Config (with new fields)
curl https://snip-production.up.railway.app/api/widget/config/YOUR_CLIENT_ID
# Verify: width, height, customCss, theme fields

# 3. Widget Loads
curl -I https://widget-sigma-sage.vercel.app/widget.js
# Expected: 200 OK

# 4. Dashboard Loads
curl -I https://snip.mothership-ai.com
# Expected: 200 OK

# 5. Migration Complete
# Check Railway logs for: "✅ Migration check: Customization columns verified/added"
```

---

## 🎉 Deployment Complete

**Status**: ✅ **ALL SYSTEMS DEPLOYED**

Once all verification steps pass:
- ✅ Database migration complete
- ✅ Backend deployed with all enhancements
- ✅ Widget deployed with customization support
- ✅ Dashboard deployed with all features

**System is production-ready!** 🚀

---

## 📞 Support

If deployment fails:
1. Check Railway logs (backend)
2. Check Vercel logs (widget/dashboard)
3. Verify environment variables
4. Check migration status
5. Review this guide's troubleshooting section

**Documentation**:
- Migration Guide: `DATABASE_MIGRATION_NEEDED_CUSTOMIZATION.md`
- Deployment Guide: `DEPLOYMENT_READY.md`
- Implementation Summary: `COMPLETE_SYSTEM_READY.md`

---

**Last Updated**: 2026-01-16  
**Status**: ✅ **READY FOR DEPLOYMENT**
