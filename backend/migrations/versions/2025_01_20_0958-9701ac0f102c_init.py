"""init

Revision ID: 9701ac0f102c
Revises: 
Create Date: 2025-01-20 09:58:31.414245

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = '9701ac0f102c'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('company',
                    sa.Column(
                        'name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
                    sa.Column(
                        'description', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=False),
                    sa.Column('updated_at', sa.DateTime(), nullable=False),
                    sa.Column('created_by', sqlmodel.sql.sqltypes.AutoString(),
                              nullable=True),
                    sa.Column('updated_by', sqlmodel.sql.sqltypes.AutoString(),
                              nullable=True),
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_company_id'), 'company', ['id'], unique=False)
    op.create_table('dataentry',
                    sa.Column(
                        'name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
                    sa.Column(
                        'description', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=False),
                    sa.Column('updated_at', sa.DateTime(), nullable=False),
                    sa.Column('created_by', sqlmodel.sql.sqltypes.AutoString(),
                              nullable=True),
                    sa.Column('updated_by', sqlmodel.sql.sqltypes.AutoString(),
                              nullable=True),
                    sa.Column('identifier', sqlmodel.sql.sqltypes.AutoString(),
                              nullable=False),
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column(
                        'data', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_dataentry_id'), 'dataentry', ['id'], unique=False)
    op.create_table('form',
                    sa.Column(
                        'name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
                    sa.Column(
                        'description', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=False),
                    sa.Column('updated_at', sa.DateTime(), nullable=False),
                    sa.Column('created_by', sqlmodel.sql.sqltypes.AutoString(),
                              nullable=True),
                    sa.Column('updated_by', sqlmodel.sql.sqltypes.AutoString(),
                              nullable=True),
                    sa.Column('items', postgresql.JSONB(
                        astext_type=sa.Text()), nullable=False),
                    sa.Column('i18n', postgresql.JSONB(
                        astext_type=sa.Text()), nullable=False),
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_form_id'), 'form', ['id'], unique=False)
    op.create_table('accesslog',
                    sa.Column(
                        'name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
                    sa.Column(
                        'description', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=False),
                    sa.Column('updated_at', sa.DateTime(), nullable=False),
                    sa.Column('created_by', sqlmodel.sql.sqltypes.AutoString(),
                              nullable=True),
                    sa.Column('updated_by', sqlmodel.sql.sqltypes.AutoString(),
                              nullable=True),
                    sa.Column('username', sqlmodel.sql.sqltypes.AutoString(),
                              nullable=False),
                    sa.Column(
                        'method', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
                    sa.Column('timestamp', sa.DateTime(), nullable=False),
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('data_entry_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(
                        ['data_entry_id'], ['dataentry.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_accesslog_id'), 'accesslog', ['id'], unique=False)
    op.create_table('formrevision',
                    sa.Column(
                        'name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
                    sa.Column(
                        'description', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=False),
                    sa.Column('updated_at', sa.DateTime(), nullable=False),
                    sa.Column('created_by', sqlmodel.sql.sqltypes.AutoString(),
                              nullable=True),
                    sa.Column('updated_by', sqlmodel.sql.sqltypes.AutoString(),
                              nullable=True),
                    sa.Column('items', postgresql.JSONB(
                        astext_type=sa.Text()), nullable=False),
                    sa.Column('i18n', postgresql.JSONB(
                        astext_type=sa.Text()), nullable=False),
                    sa.Column('version', sa.Integer(), nullable=False),
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('form_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['form_id'], ['form.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_formrevision_id'),
                    'formrevision', ['id'], unique=False)
    op.create_table('campaign',
                    sa.Column(
                        'name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
                    sa.Column(
                        'description', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=False),
                    sa.Column('updated_at', sa.DateTime(), nullable=False),
                    sa.Column('created_by', sqlmodel.sql.sqltypes.AutoString(),
                              nullable=True),
                    sa.Column('updated_by', sqlmodel.sql.sqltypes.AutoString(),
                              nullable=True),
                    sa.Column(
                        'url', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('form_revision_id',
                              sa.Integer(), nullable=False),
                    sa.Column('company_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['company_id'], ['company.id'], ),
                    sa.ForeignKeyConstraint(['form_revision_id'], [
                                            'formrevision.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_campaign_id'), 'campaign', ['id'], unique=False)
    op.create_table('participant',
                    sa.Column(
                        'name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
                    sa.Column(
                        'description', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=False),
                    sa.Column('updated_at', sa.DateTime(), nullable=False),
                    sa.Column('created_by', sqlmodel.sql.sqltypes.AutoString(),
                              nullable=True),
                    sa.Column('updated_by', sqlmodel.sql.sqltypes.AutoString(),
                              nullable=True),
                    sa.Column(
                        'token', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
                    sa.Column('identifier', sqlmodel.sql.sqltypes.AutoString(),
                              nullable=False),
                    sa.Column(
                        'status', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('campaign_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(
                        ['campaign_id'], ['campaign.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_participant_id'),
                    'participant', ['id'], unique=False)
    op.create_table('casereport',
                    sa.Column(
                        'name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
                    sa.Column(
                        'description', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=False),
                    sa.Column('updated_at', sa.DateTime(), nullable=False),
                    sa.Column('created_by', sqlmodel.sql.sqltypes.AutoString(),
                              nullable=True),
                    sa.Column('updated_by', sqlmodel.sql.sqltypes.AutoString(),
                              nullable=True),
                    sa.Column('identifier', sqlmodel.sql.sqltypes.AutoString(),
                              nullable=False),
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column(
                        'data', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
                    sa.Column('form_revision_id',
                              sa.Integer(), nullable=False),
                    sa.Column('participant_id', sa.Integer(), nullable=False),
                    sa.Column('campaign_id', sa.Integer(), nullable=False),
                    sa.Column('company_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(
                        ['campaign_id'], ['campaign.id'], ),
                    sa.ForeignKeyConstraint(['company_id'], ['company.id'], ),
                    sa.ForeignKeyConstraint(['form_revision_id'], [
                                            'formrevision.id'], ),
                    sa.ForeignKeyConstraint(['participant_id'], [
                                            'participant.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_casereport_id'),
                    'casereport', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_casereport_id'), table_name='casereport')
    op.drop_table('casereport')
    op.drop_index(op.f('ix_participant_id'), table_name='participant')
    op.drop_table('participant')
    op.drop_index(op.f('ix_campaign_id'), table_name='campaign')
    op.drop_table('campaign')
    op.drop_index(op.f('ix_formrevision_id'), table_name='formrevision')
    op.drop_table('formrevision')
    op.drop_index(op.f('ix_accesslog_id'), table_name='accesslog')
    op.drop_table('accesslog')
    op.drop_index(op.f('ix_form_id'), table_name='form')
    op.drop_table('form')
    op.drop_index(op.f('ix_dataentry_id'), table_name='dataentry')
    op.drop_table('dataentry')
    op.drop_index(op.f('ix_company_id'), table_name='company')
    op.drop_table('company')
    # ### end Alembic commands ###
