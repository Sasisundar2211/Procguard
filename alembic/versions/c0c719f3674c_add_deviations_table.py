"""add_deviations_table

Revision ID: c0c719f3674c
Revises: 679e4d7ad3a0
Create Date: 2026-01-08 12:48:37.441750

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c0c719f3674c'
down_revision: Union[str, None] = '679e4d7ad3a0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'deviations',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('batch_id', sa.UUID(), nullable=False),
        sa.Column('stage', sa.String(), nullable=False),
        sa.Column('deviation_type', sa.String(), nullable=False),
        sa.Column('approved_by', sa.String(), nullable=False),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('valid_from_day', sa.Integer(), nullable=False),
        sa.Column('valid_until_day', sa.Integer(), nullable=False),
        sa.Column('superseded_by_lir', sa.Boolean(), nullable=False),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['batch_id'], ['batches.batch_id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("deviation_type IN ('TIME','SEQUENCE','RULE')", name='_deviation_type_check')
    )


def downgrade() -> None:
    op.drop_table('deviations')
