import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.models.batch import Batch
from app.models.procedure import Procedure, ProcedureStep
from app.core.fsm import State
from datetime import datetime, timezone

# Use the test database
DATABASE_URL = "postgresql+pg8000://djtaylor@localhost/procguard_test"

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    engine = create_engine(DATABASE_URL)
    # Force clean schema at start of session
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    # 2. Add Enforcement Triggers (Required for Immutability tests)
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE OR REPLACE FUNCTION forbid_audit_mutation()
            RETURNS trigger AS $$
            BEGIN
                RAISE EXCEPTION 'Audit logs are immutable';
            END;
            $$ LANGUAGE plpgsql;
        """))
        conn.execute(text("""
            CREATE TRIGGER audit_no_update
            BEFORE UPDATE OR DELETE ON audit_logs
            FOR EACH ROW EXECUTE FUNCTION forbid_audit_mutation();
        """))
        conn.commit()
    
    # Standardize: Procedures are legislation. They MUST exist for batches to refer to them.
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    with Session() as session:
        procedure_id = uuid.UUID("11111111-1111-1111-1111-111111111111")
        proc = Procedure(
            procedure_id=procedure_id,
            name="Test Procedure",
            description="Enterprise Test Script",
            version=1,
            created_at=datetime.now(timezone.utc)
        )
        session.add(proc)
        session.commit()

    # Apply global dependency override for FastAPI tests
    from app.main import app
    from app.api.deps import get_db
    
    def override_get_db():
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
            
    app.dependency_overrides[get_db] = override_get_db
    
    yield engine
    app.dependency_overrides.clear()
    engine.dispose()

@pytest.fixture(scope="function")
def db_session(setup_test_db):
    engine = setup_test_db
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    # Fast truncate for function level isolation
    tables = ", ".join(Base.metadata.tables.keys())
    if tables:
        session.execute(text(f"TRUNCATE TABLE {tables} CASCADE;"))
        session.commit()

    yield session
    
    session.rollback()
    session.close()


@pytest.fixture
def batch(db_session):
    # 1. Create Normalized Procedure
    procedure_id = uuid.UUID("11111111-1111-1111-1111-111111111111")
    proc = Procedure(
        procedure_id=procedure_id,
        name="Test Procedure",
        description="Enterprise Test Script",
        version=1,
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(proc)
    
    # 2. Add Step
    step = ProcedureStep(
        step_id=uuid.uuid4(),
        procedure_id=procedure_id,
        step_order=1,
        step_name="Step 1",
        requires_approval=True,
        approver_role="SUPERVISOR"
    )
    db_session.add(step)
    db_session.flush()

    # 3. Create Batch
    batch = Batch(
        batch_id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
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
    procedure_id = uuid.UUID("11111111-1111-1111-1111-111111111111")
    
    # Check if exists
    proc = db_session.query(Procedure).get(procedure_id)
    if not proc:
        proc = Procedure(
            procedure_id=procedure_id,
            name="Test Procedure",
            description="Enterprise Test Script",
            version=1,
            created_at=datetime.now(timezone.utc)
        )
        db_session.add(proc)

    batch = Batch(
        batch_id=uuid.UUID("00000000-0000-0000-0000-000000000002"),
        procedure_id=procedure_id,
        procedure_version=1,
        current_state=State.COMPLETED.value,
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(batch)
    db_session.commit()
    return batch

import uuid # Ensure uuid is available for fixtures
