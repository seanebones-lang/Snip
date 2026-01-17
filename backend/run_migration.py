#!/usr/bin/env python3
"""
Database Migration Script
Adds AI provider columns to client_configs table
"""
import os
import sys
from sqlalchemy import create_engine, text

def run_migration():
    # Get DATABASE_URL from environment (Railway provides this)
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set")
        sys.exit(1)
    
    # Convert postgres:// to postgresql:// if needed (for SQLAlchemy)
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    print(f"Connecting to database...")
    engine = create_engine(database_url)
    
    migration_sql = """
    ALTER TABLE client_configs
    ADD COLUMN IF NOT EXISTS ai_provider VARCHAR(50),
    ADD COLUMN IF NOT EXISTS ai_api_key TEXT,
    ADD COLUMN IF NOT EXISTS ai_model VARCHAR(100);
    """
    
    try:
        with engine.connect() as conn:
            print("Running migration...")
            conn.execute(text(migration_sql))
            conn.commit()
            print("✅ Migration completed successfully!")
            
            # Verify columns were added
            verify_sql = """
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'client_configs' 
            AND column_name IN ('ai_provider', 'ai_api_key', 'ai_model');
            """
            result = conn.execute(text(verify_sql))
            rows = result.fetchall()
            
            if len(rows) == 3:
                print("✅ All columns verified:")
                for row in rows:
                    print(f"   - {row[0]} ({row[1]})")
                return True
            else:
                print(f"⚠️ Expected 3 columns, found {len(rows)}")
                return False
                
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        engine.dispose()

if __name__ == '__main__':
    success = run_migration()
    sys.exit(0 if success else 1)
