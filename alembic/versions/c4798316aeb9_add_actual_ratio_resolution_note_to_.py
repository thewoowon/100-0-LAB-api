"""add_actual_ratio_resolution_note_to_casestatus

Revision ID: c4798316aeb9
Revises: 38c06888a0c5
Create Date: 2026-03-11 00:40:45.614240

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c4798316aeb9'
down_revision: Union[str, None] = '38c06888a0c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('casestatus', sa.Column('actual_ratio', sa.String(), nullable=True))
    op.add_column('casestatus', sa.Column('resolution_note', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('casestatus', 'resolution_note')
    op.drop_column('casestatus', 'actual_ratio')
