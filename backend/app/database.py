"""
Database connection and session management
"""
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import get_settings

settings = get_settings()

# Create engine - use asyncpg for async support in production
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency for getting database sessions"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables and run migrations"""
    # Create all tables first - this will create tables with all columns defined in models
    # If table already exists without new columns, we'll add them via migration below
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables verified/created")
    except Exception as e:
        print(f"⚠️ Table creation warning: {e}")
        # Continue anyway - migration below will handle missing columns
    
    # Run migrations: Add columns if they don't exist
    # PostgreSQL supports IF NOT EXISTS for columns (9.5+)
    migrations = [
        {
            "name": "AI provider columns",
            "sql": """
                DO $$ 
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                   WHERE table_name = 'client_configs' AND column_name = 'ai_provider') THEN
                        ALTER TABLE client_configs ADD COLUMN ai_provider VARCHAR(50);
                    END IF;
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                   WHERE table_name = 'client_configs' AND column_name = 'ai_api_key') THEN
                        ALTER TABLE client_configs ADD COLUMN ai_api_key TEXT;
                    END IF;
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                   WHERE table_name = 'client_configs' AND column_name = 'ai_model') THEN
                        ALTER TABLE client_configs ADD COLUMN ai_model VARCHAR(100);
                    END IF;
                END $$;
            """
        },
        {
            "name": "Customization columns",
            "sql": """
                DO $$ 
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                   WHERE table_name = 'client_configs' AND column_name = 'widget_width') THEN
                        ALTER TABLE client_configs ADD COLUMN widget_width INTEGER NULL;
                    END IF;
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                   WHERE table_name = 'client_configs' AND column_name = 'widget_height') THEN
                        ALTER TABLE client_configs ADD COLUMN widget_height INTEGER NULL;
                    END IF;
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                   WHERE table_name = 'client_configs' AND column_name = 'custom_css') THEN
                        ALTER TABLE client_configs ADD COLUMN custom_css TEXT NULL;
                    END IF;
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                   WHERE table_name = 'client_configs' AND column_name = 'theme') THEN
                        ALTER TABLE client_configs ADD COLUMN theme VARCHAR(50) NULL;
                    END IF;
                END $$;
            """
        }
    ]
    
    for migration in migrations:
        try:
            with engine.begin() as conn:
                # Only run if client_configs table exists
                check_table = text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'client_configs'
                    );
                """)
                table_exists = conn.execute(check_table).scalar()
                
                if table_exists:
                    conn.execute(text(migration["sql"]))
                    print(f"✅ Migration: {migration['name']} verified/added")
                else:
                    print(f"⚠️ Migration: {migration['name']} skipped (table not created yet)")
        except Exception as e:
            # Log error but don't crash - migration might already be done
            print(f"⚠️ Migration ({migration['name']}) check (non-fatal): {e}")
            # Continue with other migrations

# Auto-migration enabled
