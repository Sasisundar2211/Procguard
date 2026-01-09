"""phase_1_core_schema_immutability

Revision ID: 582e852a1173
Revises: 
Create Date: 2026-01-05 16:32:00.679576

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '582e852a1173'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # 1. Extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')

    # 2. Procedures (Immutable Law)
    op.execute("""
    CREATE TABLE procedures (
        procedure_id UUID NOT NULL,
        version INTEGER NOT NULL CHECK (version > 0),

        required_steps JSONB NOT NULL,
        approval_requirements JSONB NOT NULL,
        sequence_constraints JSONB NOT NULL,

        published_at TIMESTAMPTZ NOT NULL DEFAULT now(),

        PRIMARY KEY (procedure_id, version)
    );
    """)

    op.execute("""
    ALTER TABLE procedures
    ADD CONSTRAINT required_steps_is_array
    CHECK (jsonb_typeof(required_steps) = 'array');
    """)

    op.execute("""
    ALTER TABLE procedures
    ADD CONSTRAINT required_steps_not_empty
    CHECK (jsonb_array_length(required_steps) > 0);
    """)

    op.execute("""
    CREATE OR REPLACE FUNCTION forbid_procedure_mutation()
    RETURNS trigger AS $$
    BEGIN
        RAISE EXCEPTION 'Procedures are immutable once published';
    END;
    $$ LANGUAGE plpgsql;
    """)

    op.execute("""
    CREATE TRIGGER procedures_no_update
    BEFORE UPDATE OR DELETE ON procedures
    FOR EACH ROW EXECUTE FUNCTION forbid_procedure_mutation();
    """)

    # 3. Batches (Single Source of Truth)
    op.execute("""
    CREATE TABLE batches (
        batch_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

        procedure_id UUID NOT NULL,
        procedure_version INTEGER NOT NULL,

        current_state TEXT NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

        FOREIGN KEY (procedure_id, procedure_version)
            REFERENCES procedures(procedure_id, version)
    );
    """)

    op.execute("""
    ALTER TABLE batches
    ADD CONSTRAINT valid_batch_state
    CHECK (
        current_state IN (
            'CREATED',
            'IN_PROGRESS',
            'AWAITING_APPROVAL',
            'APPROVED',
            'COMPLETED',
            'VIOLATED',
            'REJECTED'
        )
    );
    """)

    # 4. Batch Events (Append-only)
    op.execute("""
    CREATE TABLE batch_events (
        event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        batch_id UUID NOT NULL,
        event_type TEXT NOT NULL,
        payload JSONB NOT NULL,
        occurred_at TIMESTAMPTZ NOT NULL,
        FOREIGN KEY (batch_id) REFERENCES batches(batch_id)
    );
    """)

    op.execute("""
    CREATE INDEX idx_batch_events_batch_id
    ON batch_events(batch_id);
    """)

    op.execute("""
    CREATE OR REPLACE FUNCTION forbid_event_mutation()
    RETURNS trigger AS $$
    BEGIN
        RAISE EXCEPTION 'Events are append-only';
    END;
    $$ LANGUAGE plpgsql;
    """)

    op.execute("""
    CREATE TRIGGER events_no_update
    BEFORE UPDATE OR DELETE ON batch_events
    FOR EACH ROW EXECUTE FUNCTION forbid_event_mutation();
    """)

    # 5. Violations (Irreversible)
    op.execute("""
    CREATE TABLE violations (
        violation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        batch_id UUID NOT NULL,
        rule TEXT NOT NULL,
        detected_at TIMESTAMPTZ NOT NULL,
        FOREIGN KEY (batch_id) REFERENCES batches(batch_id)
    );
    """)

    op.execute("""
    CREATE INDEX idx_violations_batch_id
    ON violations(batch_id);
    """)

    op.execute("""
    CREATE OR REPLACE FUNCTION forbid_violation_mutation()
    RETURNS trigger AS $$
    BEGIN
        RAISE EXCEPTION 'Violations are immutable';
    END;
    $$ LANGUAGE plpgsql;
    """)

    op.execute("""
    CREATE TRIGGER violations_no_update
    BEFORE UPDATE OR DELETE ON violations
    FOR EACH ROW EXECUTE FUNCTION forbid_violation_mutation();
    """)

    # 6. Audit Logs (Courtroom Safe)
    op.execute("""
    CREATE TABLE audit_logs (
        audit_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        batch_id UUID NOT NULL,
        expected_state TEXT NOT NULL,
        attempted_event TEXT NOT NULL,
        actual_outcome TEXT NOT NULL,
        actor TEXT NOT NULL,
        occurred_at TIMESTAMPTZ NOT NULL,
        violation_id UUID,
        FOREIGN KEY (batch_id) REFERENCES batches(batch_id),
        FOREIGN KEY (violation_id) REFERENCES violations(violation_id)
    );
    """)

    op.execute("""
    CREATE INDEX idx_audit_logs_batch_id
    ON audit_logs(batch_id);
    """)

    op.execute("""
    CREATE OR REPLACE FUNCTION forbid_audit_mutation()
    RETURNS trigger AS $$
    BEGIN
        RAISE EXCEPTION 'Audit logs are immutable';
    END;
    $$ LANGUAGE plpgsql;
    """)

    op.execute("""
    CREATE TRIGGER audit_no_update
    BEFORE UPDATE OR DELETE ON audit_logs
    FOR EACH ROW EXECUTE FUNCTION forbid_audit_mutation();
    """)

def downgrade():
    op.execute("DROP TABLE IF EXISTS audit_logs CASCADE;")
    op.execute("DROP TABLE IF EXISTS violations CASCADE;")
    op.execute("DROP TABLE IF EXISTS batch_events CASCADE;")
    op.execute("DROP TABLE IF EXISTS batches CASCADE;")
    op.execute("DROP TABLE IF EXISTS procedures CASCADE;")

