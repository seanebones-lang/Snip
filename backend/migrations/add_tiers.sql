-- Add standard and premium to tier enum

-- Create new enum with all values
CREATE TYPE tierenum_new AS ENUM ('basic', 'standard', 'premium');

-- Update table to use new enum
ALTER TABLE clients ALTER COLUMN tier TYPE tierenum_new USING tier::text::tierenum_new;

-- Drop old enum
DROP TYPE tierenum;

-- Rename new enum
ALTER TYPE tierenum_new RENAME TO tierenum;