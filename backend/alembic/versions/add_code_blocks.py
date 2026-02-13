"""Add program blocks columns

Revision ID: add_code_blocks
Revises: 
Create Date: 2026-02-02

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = 'add_code_blocks'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to generated_codes table
    with op.batch_alter_table('generated_codes', schema=None) as batch_op:
        batch_op.add_column(sa.Column('program_blocks', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('functions', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('function_blocks', sa.JSON(), nullable=True))


def downgrade():
    # Remove the columns if rolling back
    with op.batch_alter_table('generated_codes', schema=None) as batch_op:
        batch_op.drop_column('function_blocks')
        batch_op.drop_column('functions')
        batch_op.drop_column('program_blocks')
