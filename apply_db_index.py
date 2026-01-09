
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, ProgrammingError
import time

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/procguard" # Default
try:
    with open(".env", "r") as f:
        for line in f:
            if line.startswith("DATABASE_URL="):
                DATABASE_URL = line.strip().split("=", 1)[1]
except:
    pass

def apply_index():
    engine = create_engine(DATABASE_URL, isolation_level="AUTOCOMMIT") # Needed for CONCURRENTLY
    try:
        with engine.connect() as conn:
            # Check if index exists
            check_sql = "SELECT indexname FROM pg_indexes WHERE tablename = 'boards' AND indexname = 'idx_boards_title_active'"
            result = conn.execute(text(check_sql))
            if result.fetchone():
                print("Index 'idx_boards_title_active' ALREADY EXISTS.")
                return

            print("Creating index 'idx_boards_title_active' safely...")
            # Create Unique Index on Title where Status is ACTIVE
            # This allows re-using names if old ones are DELETED/DEPRECATED
            sql = "CREATE UNIQUE INDEX CONCURRENTLY idx_boards_title_active ON boards (title) WHERE status = 'ACTIVE'"
            conn.execute(text(sql))
            print("Index created successfully.")
            
    except ProgrammingError as e:
        if "duplicate table" in str(e) or "recursion" in str(e):
            print(f"Index creation failed: {e}")
        else:
            print(f"Programming Error: {e}")
    except Exception as e:
        print(f"Error applying index: {e}")

if __name__ == "__main__":
    apply_index()
