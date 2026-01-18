#!/usr/bin/env python3
"""
Database Migration Script: Add Customization Columns
Date: 2026-01-16
Purpose: Add widget_width, widget_height, custom_css, and theme columns to client_configs table

Usage:
    python run_customization_migration.py

This script safely adds new columns to the client_configs table.
It uses IF NOT EXISTS to prevent errors if columns already exist.
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment
database_url = os.getenv("DATABASE_URL")

if not database_url:
    print("❌ Error: DATABASE_URL environment variable not set")
    print("Please set DATABASE_URL before running migration")
    sys.exit(1)

print(f"🔗 Connecting to database...")
print(f"   Database: {database_url.split('@')[1] if '@' in database_url else 'configured'}")

try:
    # Create engine
    engine = create_engine(database_url, pool_pre_ping=True)
    
    # Migration SQL
    migration_sql = """
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
    """
    
    print(f"\n🔄 Running migration...")
    
    with engine.begin() as conn:
        # Execute migration
        conn.execute(text(migration_sql))
        print("✅ Migration executed successfully")
    
    # Verify migration
    print(f"\n🔍 Verifying migration...")
    
    verification_sql = """
    SELECT column_name, data_type, is_nullable, column_default
    FROM information_schema.columns
    WHERE table_name = 'client_configs'
    AND column_name IN ('widget_width', 'widget_height', 'custom_css', 'theme')
    ORDER BY column_name;
    """
    
    with engine.connect() as conn:
        result = conn.execute(text(verification_sql))
        rows = result.fetchall()
        
        if len(rows) == 4:
            print("✅ Verification successful - All 4 columns exist:")
            print()
            print(f"   {'Column Name':<20} {'Data Type':<25} {'Nullable':<10} {'Default'}")
            print(f"   {'-'*70}")
            for row in rows:
                print(f"   {row[0]:<20} {row[1]:<25} {row[2]:<10} {row[3] or 'NULL'}")
            print()
            print("✅ Migration complete - All columns added successfully!")
            sys.exit(0)
        else:
            print(f"⚠️  Warning: Expected 4 columns, found {len(rows)}")
            if rows:
                print("Columns found:")
                for row in rows:
                    print(f"   - {row[0]}")
            sys.exit(1)
            
except Exception as e:
    print(f"❌ Migration failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
