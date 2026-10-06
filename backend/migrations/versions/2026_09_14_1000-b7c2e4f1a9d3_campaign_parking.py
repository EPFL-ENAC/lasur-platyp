"""campaign-parking

Revision ID: b7c2e4f1a9d3
Revises: 9fad38829320
Create Date: 2026-09-14 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7c2e4f1a9d3'
down_revision: Union[str, None] = '9fad38829320'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('campaign', sa.Column(
        'parking_provided', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column('campaign', sa.Column(
        'parking_paid', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column('campaign', sa.Column(
        'parking_details', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('campaign', 'parking_details')
    op.drop_column('campaign', 'parking_paid')
    op.drop_column('campaign', 'parking_provided')
