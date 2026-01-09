"""enforce_single_approval_per_step

Revision ID: ef6ea0cb8d5c
Revises: 582e852a1173
Create Date: 2026-01-06 10:05:31.752779

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ef6ea0cb8d5c'
down_revision: Union[str, None] = '582e852a1173'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute(
        """
        CREATE UNIQUE INDEX one_approval_per_step
        ON batch_events (
            batch_id,
            (payload->>'step_id')
        )
        WHERE event_type = 'approve_step';
        """
    )


def downgrade():
    op.execute(
        """
        DROP INDEX IF EXISTS one_approval_per_step;
        """
    )

