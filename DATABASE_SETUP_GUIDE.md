# Database Setup Guide for Railway

## Issue

The API is returning "Internal Server Error" when creating clients because the PostgreSQL database isn't configured on Railway.

## Solution: Add PostgreSQL Database on Railway

### Step-by-Step Instructions

#### Step 1: Go to Your Railway Project

1. Log into [Railway Dashboard](https://railway.app)
2. Open your Snip project

#### Step 2: Add PostgreSQL Service

1. Click **"+ New"** button
2. Select **"Database"** from the dropdown
3. Select **"Add PostgreSQL"**
4. Railway will create a PostgreSQL database service

#### Step 3: Link to Backend Service

1. Railway should automatically detect the backend service needs the database
2. If not, click on your backend service
3. Go to **"Settings"** tab
4. Under **"Variables"**, Railway should automatically add `DATABASE_URL`
5. If not, manually add:
   - **Name**: `DATABASE_URL`
   - **Value**: Railway will provide this (starts with `postgresql://...`)

#### Step 4: Verify Connection

1. **Redeploy** your backend service (Railway should auto-deploy)
2. Check **Logs** tab - should see successful database connection
3. Wait for deployment to complete

#### Step 5: Test Client Creation

Once database is connected, test creating a client:

```bash
curl -X POST https://snip-production.up.railway.app/api/clients \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-email@example.com",
    "company_name": "Your Company Name"
  }'
```

**Expected Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "your-email@example.com",
  "company_name": "Your Company Name",
  "api_key": "snip_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "tier": "basic",
  "created_at": "2026-01-16T20:00:00Z"
}
```

#### Step 6: Use API Key in Dashboard

1. Copy the `api_key` from the response
2. Go to dashboard login page
3. Paste API key and click "Access Dashboard"
4. You should now see the dashboard with pricing cards!

---

## Verification Checklist

- [ ] PostgreSQL service added in Railway
- [ ] `DATABASE_URL` environment variable visible in backend service
- [ ] Backend service redeployed after adding database
- [ ] Deployment logs show successful connection (no database errors)
- [ ] `/api/clients` endpoint works (returns 200, not 500)
- [ ] Can create a client and receive API key
- [ ] Can log into dashboard with API key

---

## What Happens Automatically

Once PostgreSQL is added:

1. **Database Tables Created**: The `init_db()` function runs on startup and creates all tables
2. **Connection Pooled**: SQLAlchemy handles database connections efficiently
3. **API Works**: All endpoints requiring database access will function

---

## Troubleshooting

### If Database Still Not Working

**Check Railway Logs:**
1. Go to backend service → **Logs** tab
2. Look for database connection errors
3. Verify `DATABASE_URL` is set correctly

**Common Issues:**
- Database not linked to backend service
- `DATABASE_URL` not in environment variables
- Database service not started
- Network connectivity issues

**Solution:**
- Unlink and re-link database service
- Manually add `DATABASE_URL` in backend service variables
- Restart backend service

---

## After Database is Set Up

Once the database is working:

1. ✅ Create clients via API
2. ✅ Get API keys for dashboard access
3. ✅ View pricing cards on dashboard
4. ✅ Manage widget configurations
5. ✅ Track usage statistics

---

**The database is the foundation - everything else depends on it working correctly!**
