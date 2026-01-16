# FIX: Delete Extra PostgreSQL Databases

## Problem
Three PostgreSQL databases were created, but you only need ONE.

## Solution: Delete 2 Extra Databases via Railway Dashboard

Since Railway CLI doesn't support deleting services, you must use the web dashboard:

### Step 1: Open Railway Project
Go to: https://railway.app/project/02602f57-7c35-468a-abb3-678af0f43fe1

### Step 2: Identify PostgreSQL Services
You'll see multiple services listed. Look for services named:
- "PostgreSQL" 
- "postgres"
- Or similar database service names

### Step 3: Delete Extra Databases (Keep Only ONE)
For EACH extra PostgreSQL service (delete 2, keep 1):

1. Click on the PostgreSQL service name
2. Click the "Settings" tab (or gear icon)
3. Scroll to the bottom
4. Click "Delete Service" or "Remove Service" button
5. Confirm the deletion

**IMPORTANT:** 
- Keep the PostgreSQL service that has `DATABASE_URL` already set
- Or keep the first/oldest one if unsure
- Delete the other 2

### Step 4: Verify Only One Remains
After deleting, you should see only ONE PostgreSQL service in your project.

### Step 5: Verify DATABASE_URL is Set
Run this command:
```bash
cd /Users/nexteleven/snip/Snip/backend
railway variables | grep DATABASE_URL
```

You should see `DATABASE_URL` with a PostgreSQL connection string.

### Step 6: Redeploy Backend
```bash
cd /Users/nexteleven/snip/Snip/backend
railway redeploy
```

### Step 7: Test API
```bash
curl -X POST https://snip-production.up.railway.app/api/clients \
  -H "Content-Type: application/json" \
  -d '{"email":"test@mothership.ai","company_name":"Test Company"}'
```

Should return client data with API key (not "Internal Server Error").

---

## Why This Happened
The `railway add --database postgres` command may have been run multiple times, or Railway created multiple instances. You only need ONE database for all pricing tiers.

---

## After Fix
- ✅ Only ONE PostgreSQL service
- ✅ DATABASE_URL environment variable set
- ✅ Backend can create clients
- ✅ Dashboard works with pricing cards
