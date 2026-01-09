import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.models.batch import Batch
from app.core.fsm import State

# Use the test database
DATABASE_URL = "postgresql+pg8000://djtaylor@localhost/procguard_test"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

@pytest.fixture(scope="function")
def db_session():
    session = SessionLocal()
    
    # Clean tables before test to ensure isolation
    # TRUNCATE ... CASCADE handles FKs
    try:
        # We assume tables exist (Alembic migration ran)
        session.execute(text("TRUNCATE TABLE audit_logs, violations, batch_events, batches, procedures CASCADE;"))
        # We generally treat procedures as immutable legislation, but for tests we need clean state.
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Cleanup failed: {e}")

    yield session
    
    session.rollback()
    session.close()


@pytest.fixture
def batch(db_session):
    procedure_id = "11111111-1111-1111-1111-111111111111"
    
    # Ensure procedure exists
    # We use a robust INSERT that handles new schema
    try:
        from datetime import datetime
        now = datetime.now()
        db_session.execute(text(f"""
            INSERT INTO procedures (procedure_id, version, name, description, steps, created_at, required_steps, approval_requirements, sequence_constraints, published_at)
            VALUES (
                '{procedure_id}', 
                1, 
                'Test Procedure', 
                'Description', 
                CAST('{{"step1": {{"name": "Step 1"}}}}' AS JSONB), 
                now(),
                CAST('["step1"]' AS JSONB), 
                CAST('{{}}' AS JSONB), 
                CAST('{{}}' AS JSONB), 
                now()
            )
            ON CONFLICT DO NOTHING
        """))
        db_session.commit()
    except Exception as e:
        print(f"Fixture setup warning (procedure): {e}")
        db_session.rollback()

    from datetime import datetime, timezone
    batch = Batch(
        batch_id="00000000-0000-0000-0000-000000000001",
        procedure_id=procedure_id,
        procedure_version=1,
        current_state=State.CREATED.value,
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(batch)
    db_session.commit()
    return batch


@pytest.fixture
def completed_batch(db_session):
    procedure_id = "11111111-1111-1111-1111-111111111111"
    
    try:
        db_session.execute(text(f"""
             INSERT INTO procedures (procedure_id, version, name, description, steps, created_at, required_steps, approval_requirements, sequence_constraints, published_at)
            VALUES (
                '{procedure_id}', 
                1, 
                'Test Procedure', 
                'Description', 
                CAST('{{}}' AS JSONB), 
                now(),
                CAST('["step1"]' AS JSONB), 
                CAST('{{}}' AS JSONB), 
                CAST('{{}}' AS JSONB), 
                now()
            )
            ON CONFLICT DO NOTHING
        """))
        db_session.commit()
    except Exception:
        db_session.rollback()

    from datetime import datetime, timezone
    batch = Batch(
        batch_id="00000000-0000-0000-0000-000000000002",
        procedure_id=procedure_id,
        procedure_version=1,
        current_state=State.COMPLETED.value,
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(batch)
    db_session.commit()
    return batch
