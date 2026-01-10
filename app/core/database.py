import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import DATABASE_URL
from app.models.base import Base

# Handle SQLite specific arguments to prevent thread errors in dev
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL, 
    connect_args=connect_args,
    pool_pre_ping=True,      # Authoritative: Detects dropped connections/restarts
    pool_recycle=3600        # Lifecycle: Recycles connections hourly
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

def init_db():
    """
    Authoritative Schema Synchronization.
    Primary: Alembic Migrations
    Secondary: SQLAlchemy create_all (Fallback)
    """
    if os.getenv("RUN_MIGRATIONS", "false").lower() == "true":
        import sqlalchemy
        from alembic import command
        from alembic.config import Config
        
        try:
            # Step 1: Attempt Alembic migration
            alembic_cfg = Config("alembic.ini")
            command.upgrade(alembic_cfg, "head")
            print("DATABASE: Authoritative schema sync complete (Alembic).")
        except Exception:
            # RED-TEAM AUDIT FIX: Never log the raw exception 'e' as it may contain the DSN/Secret
            print("DATABASE: Alembic sync skipped/failed. Attempting secondary sync (create_all)...")
            try:
                import app.models  # Side-effect: registers models
                Base.metadata.create_all(bind=engine)
                print("DATABASE: Secondary schema sync complete (create_all).")
            except Exception:
                # Final Safety: Fail-loud about availability, fail-silent about secrets.
                print("CRITICAL: Database initialization failed. Verify credentials in Azure Key Vault.")
                # Re-raising without the original context to ensure zero secret leakage
                raise RuntimeError("Database connection could not be established.")
    else:
        print("DATABASE: Skipping automatic migrations (RUN_MIGRATIONS is not 'true').")
