# Database Migration Required for Customization Fields

**Date**: 2026-01-16  
**Status**: ⚠️ **Migration Required**

---

## Overview

New customization fields have been added to the `client_configs` table. A database migration is required to add these columns.

---

## New Fields Added

The following fields have been added to `ClientConfig` model:

### 1. `widget_width` (Integer, nullable)
- **Purpose**: Custom widget width in pixels
- **Range**: 200-800px (default: 380px)
- **Default**: `NULL` (uses default 380px)

### 2. `widget_height` (Integer, nullable)
- **Purpose**: Custom widget height in pixels
- **Range**: 300-1000px (default: 550px)
- **Default**: `NULL` (uses default 550px)

### 3. `custom_css` (Text, nullable)
- **Purpose**: Custom CSS for advanced widget styling
- **Max Length**: 10,000 characters
- **Default**: `NULL`

### 4. `theme` (String(50), nullable)
- **Purpose**: Theme preset selection
- **Options**: 'light', 'dark', 'auto', 'custom'
- **Default**: `NULL` (uses 'auto')

### 5. `position` (String(20))
- **Updated**: Extended pattern to support 5 positions
- **Previous**: 'bottom-right' | 'bottom-left'
- **Current**: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left' | 'center'
- **Note**: Existing values remain valid

---

## Migration SQL

Run this SQL on your PostgreSQL database:

```sql
-- Add widget_width column
ALTER TABLE client_configs 
ADD COLUMN IF NOT EXISTS widget_width INTEGER NULL;

-- Add widget_height column
ALTER TABLE client_configs 
ADD COLUMN IF NOT EXISTS widget_height INTEGER NULL;

-- Add custom_css column
ALTER TABLE client_configs 
ADD COLUMN IF NOT EXISTS custom_css TEXT NULL;

-- Add theme column
ALTER TABLE client_configs 
ADD COLUMN IF NOT EXISTS theme VARCHAR(50) NULL;

-- Note: position column already exists, just extended enum/pattern in code
-- No migration needed for position field itself
```

---

## Verification

After migration, verify the columns exist:

```sql
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'client_configs'
AND column_name IN ('widget_width', 'widget_height', 'custom_css', 'theme')
ORDER BY column_name;
```

Expected output:
```
column_name   | data_type | is_nullable | column_default
--------------+-----------+-------------+---------------
custom_css    | text      | YES         | NULL
theme         | character varying | YES | NULL
widget_height | integer   | YES         | NULL
widget_width  | integer   | YES         | NULL
```

---

## Backward Compatibility

✅ **Fully backward compatible**

- All new fields are nullable
- Default behavior when `NULL`: Use system defaults
- Existing widgets continue working without changes
- Migration is non-breaking

---

## Model Changes

**File**: `backend/app/models.py`

```python
# New fields in ClientConfig model (lines 105-109)
widget_width = Column(Integer, nullable=True)
widget_height = Column(Integer, nullable=True)
custom_css = Column(Text, nullable=True)
theme = Column(String(50), nullable=True)
```

---

## API Changes

**No breaking changes** - All new fields are optional:

### WidgetConfig Response
- Now includes: `width`, `height`, `customCss`, `theme` (all optional)
- Backward compatible: Widgets can ignore unknown fields

### ConfigUpdate Request
- New optional fields: `widget_width`, `widget_height`, `custom_css`, `theme`
- All existing fields remain unchanged

---

## Testing After Migration

1. **Verify columns exist**: Run verification SQL above
2. **Test API**: Create/update config with new fields
3. **Test widget**: Verify widget uses new customization options
4. **Test defaults**: Verify NULL values use system defaults

---

## Rollback (if needed)

If rollback is necessary, these columns can be dropped:

```sql
ALTER TABLE client_configs DROP COLUMN IF EXISTS widget_width;
ALTER TABLE client_configs DROP COLUMN IF EXISTS widget_height;
ALTER TABLE client_configs DROP COLUMN IF EXISTS custom_css;
ALTER TABLE client_configs DROP COLUMN IF EXISTS theme;
```

**Note**: This will remove all customization settings. Data will be lost.

---

## Status

- ✅ **Code Ready**: All models, schemas, and API updated
- ✅ **Widget Ready**: Widget supports all new options
- ✅ **Dashboard Ready**: UI controls for all fields
- ⚠️ **Migration Pending**: Run SQL migration before deploying

---

**Next Step**: Run the migration SQL on production database before deploying new code.
