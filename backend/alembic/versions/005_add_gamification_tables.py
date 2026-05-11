"""Add gamification tables for review likes and unlocked books

Revision ID: 005
Revises: 004
Create Date: 2026-05-09

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '005'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add like_count to reviews table
    op.add_column('reviews', sa.Column('like_count', sa.Integer(), nullable=False, server_default='0'))
    op.create_index('ix_reviews_like_count', 'reviews', ['like_count'])
    
    # Create review_likes table (many-to-many: reviews <-> users)
    op.create_table(
        'review_likes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('review_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['review_id'], ['reviews.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('review_id', 'user_id', name='uq_review_user_like')
    )
    op.create_index('ix_review_likes_review_id', 'review_likes', ['review_id'])
    op.create_index('ix_review_likes_user_id', 'review_likes', ['user_id'])
    
    # Create unlocked_books table (tracks which books users have unlocked)
    op.create_table(
        'unlocked_books',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('edition_id', sa.Integer(), nullable=False),
        sa.Column('review_id', sa.Integer(), nullable=False),
        sa.Column('unlocked_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['edition_id'], ['editions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['review_id'], ['reviews.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'edition_id', name='uq_user_edition_unlock')
    )
    op.create_index('ix_unlocked_books_user_id', 'unlocked_books', ['user_id'])
    op.create_index('ix_unlocked_books_edition_id', 'unlocked_books', ['edition_id'])
    op.create_index('ix_unlocked_books_review_id', 'unlocked_books', ['review_id'])


def downgrade() -> None:
    op.drop_index('ix_unlocked_books_review_id', table_name='unlocked_books')
    op.drop_index('ix_unlocked_books_edition_id', table_name='unlocked_books')
    op.drop_index('ix_unlocked_books_user_id', table_name='unlocked_books')
    op.drop_table('unlocked_books')
    
    op.drop_index('ix_review_likes_user_id', table_name='review_likes')
    op.drop_index('ix_review_likes_review_id', table_name='review_likes')
    op.drop_table('review_likes')
    
    op.drop_index('ix_reviews_like_count', table_name='reviews')
    op.drop_column('reviews', 'like_count')
