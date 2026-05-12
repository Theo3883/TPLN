"""Add sentiment analysis columns to reviews

Revision ID: 004
Revises: 003
Create Date: 2026-05-09

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add sentiment columns to reviews table
    op.add_column('reviews', sa.Column('sentiment_label', sa.String(20), nullable=True))
    op.add_column('reviews', sa.Column('sentiment_score', sa.Float, nullable=True))
    op.add_column('reviews', sa.Column('sentiment_confidence', sa.Float, nullable=True))
    
    # Create index on sentiment_label for filtering
    op.create_index('ix_reviews_sentiment_label', 'reviews', ['sentiment_label'])
    
    # Add preview_text column to editions if not exists
    op.add_column('editions', sa.Column('preview_text', sa.Text, nullable=True))


def downgrade() -> None:
    # Drop index
    op.drop_index('ix_reviews_sentiment_label', 'reviews')
    
    # Drop sentiment columns
    op.drop_column('reviews', 'sentiment_confidence')
    op.drop_column('reviews', 'sentiment_score')
    op.drop_column('reviews', 'sentiment_label')
    
    # Drop preview_text
    op.drop_column('editions', 'preview_text')
