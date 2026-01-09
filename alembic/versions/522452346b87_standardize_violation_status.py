"""standardize_violation_status

Revision ID: 522452346b87
Revises: 04223a4eeaa2
Create Date: 2026-01-08 17:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '522452346b87'
down_revision: Union[str, None] = '04223a4eeaa2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS violations_no_update ON violations")
    op.add_column('violations', sa.Column('status', sa.String(), nullable=True))
    op.execute("UPDATE violations SET status = 'OPEN' WHERE resolution_status = 'UNRESOLVED'")
    op.execute("UPDATE violations SET status = 'RESOLVED' WHERE resolution_status = 'RESOLVED'")
    op.execute("UPDATE violations SET status = 'OPEN' WHERE status IS NULL")
    op.alter_column('violations', 'status', nullable=False)
    op.drop_column('violations', 'resolution_status')
    op.execute("""
    CREATE TRIGGER violations_no_update
    BEFORE UPDATE OR DELETE ON violations
    FOR EACH ROW EXECUTE FUNCTION forbid_violation_mutation();
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS violations_no_update ON violations")
    op.add_column('violations', sa.Column('resolution_status', sa.String(), nullable=True))
    op.execute("UPDATE violations SET resolution_status = 'UNRESOLVED' WHERE status = 'OPEN'")
    op.execute("UPDATE violations SET resolution_status = 'RESOLVED' WHERE status = 'RESOLVED'")
    op.alter_column('violations', 'resolution_status', nullable=False)
    op.drop_column('violations', 'status')
    op.execute("""
    CREATE TRIGGER violations_no_update
    BEFORE UPDATE OR DELETE ON violations
    FOR EACH ROW EXECUTE FUNCTION forbid_violation_mutation();
    """)
