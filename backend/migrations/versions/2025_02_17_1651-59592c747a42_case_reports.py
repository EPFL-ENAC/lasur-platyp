"""case-reports

Revision ID: 59592c747a42
Revises: 9fd5303099d7
Create Date: 2025-02-17 16:51:52.881828

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = '59592c747a42'
down_revision: Union[str, None] = '9fd5303099d7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('casereport', sa.Column(
        'token', sqlmodel.sql.sqltypes.AutoString(), nullable=False))
    op.drop_column('casereport', 'data')
    op.add_column('casereport', sa.Column('data',
                  postgresql.JSONB(astext_type=sa.Text()),
                  nullable=True))
    op.drop_constraint('casereport_participant_id_fkey',
                       'casereport', type_='foreignkey')
    op.drop_column('casereport', 'identifier')
    op.drop_column('casereport', 'updated_at')
    op.drop_column('casereport', 'name')
    op.drop_column('casereport', 'created_by')
    op.drop_column('casereport', 'updated_by')
    op.drop_column('casereport', 'participant_id')
    op.drop_column('casereport', 'created_at')
    op.drop_column('casereport', 'description')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('casereport', sa.Column(
        'description', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('casereport', sa.Column(
        'created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False))
    op.add_column('casereport', sa.Column('participant_id',
                  sa.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('casereport', sa.Column(
        'updated_by', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('casereport', sa.Column(
        'created_by', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('casereport', sa.Column(
        'name', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('casereport', sa.Column(
        'updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False))
    op.add_column('casereport', sa.Column(
        'identifier', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.create_foreign_key('casereport_participant_id_fkey',
                          'casereport', 'participant', ['participant_id'], ['id'])
    op.alter_column('casereport', 'data',
                    existing_type=postgresql.JSONB(astext_type=sa.Text()),
                    type_=sa.VARCHAR(),
                    nullable=False)
    op.drop_column('casereport', 'token')
    # ### end Alembic commands ###
