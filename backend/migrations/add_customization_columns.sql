-- Migration: Add customization columns to client_configs table
-- Date: 2026-01-16
-- Purpose: Add widget_width, widget_height, custom_css, and theme columns

-- Add widget_width column (nullable integer, default: NULL = 380px)
ALTER TABLE client_configs 
ADD COLUMN IF NOT EXISTS widget_width INTEGER NULL;

-- Add widget_height column (nullable integer, default: NULL = 550px)
ALTER TABLE client_configs 
ADD COLUMN IF NOT EXISTS widget_height INTEGER NULL;

-- Add custom_css column (nullable text, max: 10,000 chars)
ALTER TABLE client_configs 
ADD COLUMN IF NOT EXISTS custom_css TEXT NULL;

-- Add theme column (nullable varchar(50), options: 'light', 'dark', 'auto', 'custom')
ALTER TABLE client_configs 
ADD COLUMN IF NOT EXISTS theme VARCHAR(50) NULL;

-- Note: position column already exists, just extended enum/pattern in code
-- No migration needed for position field itself

-- Verification query (run after migration to confirm):
-- SELECT column_name, data_type, is_nullable, column_default
-- FROM information_schema.columns
-- WHERE table_name = 'client_configs'
-- AND column_name IN ('widget_width', 'widget_height', 'custom_css', 'theme')
-- ORDER BY column_name;
