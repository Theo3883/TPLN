"""Add source and crawler tracking to editions

Revision ID: 003
Revises: 002
Create Date: 2026-05-09

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add source, crawler_name, and imported_at columns to editions table."""
    
    # Add source column (tracks if edition is manual or from crawler)
    op.add_column(
        'editions',
        sa.Column(
            'source',
            sa.String(20),
            nullable=False,
            server_default='manual'
        )
    )
    
    # Add crawler_name column (tracks which crawler imported the edition)
    op.add_column(
        'editions',
        sa.Column(
            'crawler_name',
            sa.String(50),
            nullable=True
        )
    )
    
    # Add imported_at column (timestamp when crawler imported the edition)
    op.add_column(
        'editions',
        sa.Column(
            'imported_at',
            sa.DateTime(timezone=True),
            nullable=True
        )
    )
    
    # Create index on source column for efficient filtering
    op.create_index(
        'ix_editions_source',
        'editions',
        ['source']
    )
    
    # Create index on crawler_name for filtering by specific crawler
    op.create_index(
        'ix_editions_crawler_name',
        'editions',
        ['crawler_name']
    )


def downgrade() -> None:
    """Remove source tracking columns from editions table."""
    
    # Drop indexes
    op.drop_index('ix_editions_crawler_name', table_name='editions')
    op.drop_index('ix_editions_source', table_name='editions')
    
    # Drop columns
    op.drop_column('editions', 'imported_at')
    op.drop_column('editions', 'crawler_name')
    op.drop_column('editions', 'source')
