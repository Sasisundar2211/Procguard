"""upgrade_violation_model

Revision ID: 04223a4eeaa2
Revises: c0c719f3674c
Create Date: 2026-01-08 13:25:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '04223a4eeaa2'
down_revision: Union[str, None] = 'c0c719f3674c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Disable immutability temporarily to allow migration
    op.execute("DROP TRIGGER IF EXISTS violations_no_update ON violations")

    # 2. Add resolution_status column
    op.add_column('violations', sa.Column('resolution_status', sa.String(), nullable=True))
    
    # 3. Migrate data from 'resolved' to 'resolution_status'
    op.execute("UPDATE violations SET resolution_status = 'RESOLVED' WHERE resolved = true")
    op.execute("UPDATE violations SET resolution_status = 'UNRESOLVED' WHERE resolved = false")
    
    # 4. Make it non-nullable
    op.alter_column('violations', 'resolution_status', nullable=False)
    
    # 5. Drop old columns
    op.drop_column('violations', 'resolved')

    # 6. Re-enable immutability (Optional, but safe for audit)
    op.execute("""
    CREATE TRIGGER violations_no_update
    BEFORE UPDATE OR DELETE ON violations
    FOR EACH ROW EXECUTE FUNCTION forbid_violation_mutation();
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS violations_no_update ON violations")
    op.add_column('violations', sa.Column('resolved', sa.Boolean(), server_default='false', nullable=False))
    op.execute("UPDATE violations SET resolved = true WHERE resolution_status = 'RESOLVED'")
    op.execute("UPDATE violations SET resolved = false WHERE resolution_status != 'RESOLVED'")
    op.drop_column('violations', 'resolution_status')
    op.execute("""
    CREATE TRIGGER violations_no_update
    BEFORE UPDATE OR DELETE ON violations
    FOR EACH ROW EXECUTE FUNCTION forbid_violation_mutation();
    """)
