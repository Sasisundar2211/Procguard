
import os
from dotenv import load_dotenv
load_dotenv()

from app.core.database import engine
from app.models.base import Base
import app.models # This triggers the imports in __init__.py

def ensure_tables():
    print("Ensuring all tables exist...")
    Base.metadata.create_all(bind=engine)
    print("Done.")

if __name__ == "__main__":
    ensure_tables()
