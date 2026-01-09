
import sys
import os
from sqlalchemy import create_engine, text

# Try to match the user's environment if possible
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+pg8000://djtaylor@localhost:5432/procguard")

def inspect_db():
    print(f"Python: {sys.executable}")
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            print("Connected to DB.")
            
            # Check columns in procedures table
            result = conn.execute(text("SELECT column_name, is_nullable FROM information_schema.columns WHERE table_name = 'procedures';"))
            print("\n--- Columns in 'procedures' ---")
            columns = [row for row in result]
            for col in columns:
                print(f"{col[0]} (Nullable: {col[1]})")

            # Check data
            result = conn.execute(text("SELECT * FROM procedures LIMIT 5;"))
            print("\n--- Data in 'procedures' (First 5) ---")
            rows = result.fetchall()
            if not rows:
                print("No rows found.")
            for row in rows:
                print(row)
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_db()
