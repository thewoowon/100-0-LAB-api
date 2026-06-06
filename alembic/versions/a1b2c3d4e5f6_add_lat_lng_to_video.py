"""add_lat_lng_to_video

Revision ID: a1b2c3d4e5f6
Revises: e96f05a8cae1
Create Date: 2026-06-06 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'e96f05a8cae1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('video', sa.Column('lat', sa.Float(), nullable=True))
    op.add_column('video', sa.Column('lng', sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column('video', 'lng')
    op.drop_column('video', 'lat')
