-- Migration: Add AI provider columns to client_configs table
-- Run this in Railway PostgreSQL database or via Railway CLI

ALTER TABLE client_configs
ADD COLUMN IF NOT EXISTS ai_provider VARCHAR(50),
ADD COLUMN IF NOT EXISTS ai_api_key TEXT,
ADD COLUMN IF NOT EXISTS ai_model VARCHAR(100);

-- Verify columns were added
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'client_configs' 
AND column_name IN ('ai_provider', 'ai_api_key', 'ai_model');
