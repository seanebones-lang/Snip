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
    # Create all tables first
    Base.metadata.create_all(bind=engine)
    
    # Run migration: Add AI provider columns if they don't exist
    try:
        with engine.begin() as conn:
            # Use IF NOT EXISTS to safely add columns (PostgreSQL 9.5+)
            migration_sql = text("""
                ALTER TABLE client_configs
                ADD COLUMN IF NOT EXISTS ai_provider VARCHAR(50),
                ADD COLUMN IF NOT EXISTS ai_api_key TEXT,
                ADD COLUMN IF NOT EXISTS ai_model VARCHAR(100);
            """)
            conn.execute(migration_sql)
            print("✅ Migration check: AI provider columns verified/added")
    except Exception as e:
        # Log error but don't crash - migration might already be done or table might not exist yet
        print(f"Migration check (non-fatal): {e}")
        pass
    
    # Run migration: Add customization columns if they don't exist
    try:
        with engine.begin() as conn:
            # Use IF NOT EXISTS to safely add columns (PostgreSQL 9.5+)
            customization_migration = text("""
                ALTER TABLE client_configs
                ADD COLUMN IF NOT EXISTS widget_width INTEGER NULL,
                ADD COLUMN IF NOT EXISTS widget_height INTEGER NULL,
                ADD COLUMN IF NOT EXISTS custom_css TEXT NULL,
                ADD COLUMN IF NOT EXISTS theme VARCHAR(50) NULL;
            """)
            conn.execute(customization_migration)
            print("✅ Migration check: Customization columns verified/added")
    except Exception as e:
        # Log error but don't crash - migration might already be done or table might not exist yet
        print(f"Customization migration check (non-fatal): {e}")
        pass

# Auto-migration enabled
