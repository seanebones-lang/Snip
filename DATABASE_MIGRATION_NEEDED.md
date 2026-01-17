# Database Migration Required

## Issue
**Error**: `column "ai_provider" of relation "client_configs" does not exist`

The backend code was updated to support multiple AI providers, but the database columns haven't been added yet.

## Required Columns

The `client_configs` table needs these new columns:
- `ai_provider` (VARCHAR(50)) - Stores which AI provider is selected
- `ai_api_key` (TEXT) - Stores the customer's AI API key
- `ai_model` (VARCHAR(100)) - Stores the AI model name

## Solution: Add Columns via Railway

### Option 1: Railway Dashboard (Recommended)

1. Go to Railway Dashboard
2. Click on your PostgreSQL service
3. Click "Data" or "Postgres" tab
4. Open the Query/Raw SQL editor
5. Run this SQL:

```sql
ALTER TABLE client_configs
ADD COLUMN IF NOT EXISTS ai_provider VARCHAR(50),
ADD COLUMN IF NOT EXISTS ai_api_key TEXT,
ADD COLUMN IF NOT EXISTS ai_model VARCHAR(100);
```

6. Click "Run" or "Execute"

### Option 2: Railway CLI

```bash
cd /Users/nexteleven/snip/Snip/backend
railway connect postgres
```

Then run the SQL from `add_ai_columns.sql`

### Option 3: psql Command Line

If you have direct database access:

```bash
psql $DATABASE_URL -f add_ai_columns.sql
```

## Verify Migration

After running the migration, verify the columns exist:

```sql
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'client_configs' 
AND column_name IN ('ai_provider', 'ai_api_key', 'ai_model');
```

Should return 3 rows.

## After Migration

Once the columns are added:
1. ✅ Backend will work correctly
2. ✅ Client creation will succeed
3. ✅ Chat endpoint will work
4. ✅ Multi-provider AI support will be functional

---

**File**: `backend/add_ai_columns.sql` contains the migration SQL.
