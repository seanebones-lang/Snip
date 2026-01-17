"""
Database connection and session management
"""
from sqlalchemy import create_engine
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
        with engine.connect() as conn:
            # Check if columns exist
            from sqlalchemy import text, inspect
            inspector = inspect(engine)
            columns = [col['name'] for col in inspector.get_columns('client_configs')]
            
            migration_needed = False
            if 'ai_provider' not in columns:
                migration_needed = True
            
            if migration_needed:
                print("Running migration: Adding AI provider columns...")
                migration_sql = text("""
                    ALTER TABLE client_configs
                    ADD COLUMN IF NOT EXISTS ai_provider VARCHAR(50),
                    ADD COLUMN IF NOT EXISTS ai_api_key TEXT,
                    ADD COLUMN IF NOT EXISTS ai_model VARCHAR(100);
                """)
                conn.execute(migration_sql)
                conn.commit()
                print("✅ Migration completed: AI provider columns added")
    except Exception as e:
        # Log error but don't crash - migration might already be done
        print(f"Migration check: {e}")
        pass
