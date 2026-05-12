"""Add cover_url to editions

Revision ID: 006
Revises: 005
Create Date: 2026-05-12

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add cover_url column to editions table."""
    op.add_column(
        'editions',
        sa.Column('cover_url', sa.String(2048), nullable=True)
    )


def downgrade() -> None:
    """Remove cover_url column from editions table."""
    op.drop_column('editions', 'cover_url')
