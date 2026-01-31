-- Add standard and enterprise to tier enum

-- Create new enum with all values
CREATE TYPE tierenum_new AS ENUM ('basic', 'standard', 'enterprise');

-- Update table to use new enum
ALTER TABLE clients ALTER COLUMN tier TYPE tierenum_new USING tier::text::tierenum_new;

-- Drop old enum
DROP TYPE tierenum;

-- Rename new enum
ALTER TYPE tierenum_new RENAME TO tierenum;