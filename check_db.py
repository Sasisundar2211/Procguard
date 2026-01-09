
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os

# Use the same DB URL as the app
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/procguard" # Guessing default
# If .env exists, I should read it. But usually defaults are standard in dev.
# Let's try to read .env first
try:
    with open(".env", "r") as f:
        for line in f:
            if line.startswith("DATABASE_URL="):
                DATABASE_URL = line.strip().split("=", 1)[1]
except:
    pass

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT title, count(*) FROM boards WHERE status = 'ACTIVE' GROUP BY title HAVING count(*) > 1"))
        dupes = result.fetchall()
        if dupes:
            print(f"FOUND DUPLICATES: {dupes}")
        else:
            print("NO DUPLICATES FOUND")
            
        # Also check if index exists
        idx = conn.execute(text("SELECT indexname FROM pg_indexes WHERE tablename = 'boards' AND indexname = 'idx_boards_title_active'"))
        if idx.fetchone():
            print("INDEX EXISTS")
        else:
            print("INDEX DOES NOT EXIST")
            
except Exception as e:
    print(f"ERROR: {e}")
