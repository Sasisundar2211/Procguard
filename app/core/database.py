from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import DATABASE_URL
from app.models.base import Base

# Handle SQLite specific arguments to prevent thread errors in dev
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

def init_db():
    """
    Guarantees table creation on startup.
    This imports app.models to ensure all SQLAlchemy models 
    are registered with Base.metadata before creating tables.
    """
    import app.models  # Side-effect: registers models
    Base.metadata.create_all(bind=engine)
