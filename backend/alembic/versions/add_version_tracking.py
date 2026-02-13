"""add version tracking to stages

Revision ID: add_version_tracking
Revises: 
Create Date: 2026-01-30

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_version_tracking'
down_revision = None  # Update this with your latest revision
branch_labels = None
depends_on = None


def upgrade():
    # Add version tracking columns to stages table
    op.add_column('stages', sa.Column('version_number', sa.String(50), server_default='1.0.0'))
    op.add_column('stages', sa.Column('last_action', sa.String(100), nullable=True))
    op.add_column('stages', sa.Column('last_action_timestamp', sa.DateTime(), nullable=True))


def downgrade():
    # Remove version tracking columns from stages table
    op.drop_column('stages', 'last_action_timestamp')
    op.drop_column('stages', 'last_action')
    op.drop_column('stages', 'version_number')
