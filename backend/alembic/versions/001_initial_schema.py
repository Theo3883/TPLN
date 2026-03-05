"""Initial schema

Revision ID: 001
Revises:
Create Date: 2025-03-05

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "authors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("normalized_name", sa.String(255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_authors_id", "authors", ["id"], unique=False)
    op.create_index("ix_authors_name", "authors", ["name"], unique=False)
    op.create_index("ix_authors_normalized_name", "authors", ["normalized_name"], unique=False)

    op.create_table(
        "books",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("normalized_title", sa.String(500), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_books_id", "books", ["id"], unique=False)
    op.create_index("ix_books_title", "books", ["title"], unique=False)
    op.create_index("ix_books_normalized_title", "books", ["normalized_title"], unique=False)

    op.create_table(
        "editions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("book_id", sa.Integer(), nullable=False),
        sa.Column("isbn", sa.String(17), nullable=True),
        sa.Column("publisher", sa.String(255), nullable=True),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("review_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["book_id"], ["books.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_editions_id", "editions", ["id"], unique=False)
    op.create_index("ix_editions_book_id", "editions", ["book_id"], unique=False)
    op.create_index("ix_editions_isbn", "editions", ["isbn"], unique=True)

    op.create_table(
        "reviewers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("identifier", sa.String(255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_reviewers_id", "reviewers", ["id"], unique=False)
    op.create_index("ix_reviewers_identifier", "reviewers", ["identifier"], unique=True)

    op.create_table(
        "edition_authors",
        sa.Column("edition_id", sa.Integer(), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["author_id"], ["authors.id"]),
        sa.ForeignKeyConstraint(["edition_id"], ["editions.id"]),
        sa.PrimaryKeyConstraint("edition_id", "author_id"),
    )

    op.create_table(
        "reviews",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("edition_id", sa.Integer(), nullable=False),
        sa.Column("reviewer_id", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("rating", sa.Float(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["edition_id"], ["editions.id"]),
        sa.ForeignKeyConstraint(["reviewer_id"], ["reviewers.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_reviews_id", "reviews", ["id"], unique=False)
    op.create_index("ix_reviews_edition_id", "reviews", ["edition_id"], unique=False)
    op.create_index("ix_reviews_reviewer_id", "reviews", ["reviewer_id"], unique=False)

    op.create_table(
        "score_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("edition_id", sa.Integer(), nullable=False),
        sa.Column("old_score", sa.Float(), nullable=True),
        sa.Column("new_score", sa.Float(), nullable=True),
        sa.Column("reason", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["edition_id"], ["editions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_score_events_id", "score_events", ["id"], unique=False)
    op.create_index("ix_score_events_edition_id", "score_events", ["edition_id"], unique=False)


def downgrade() -> None:
    op.drop_table("score_events")
    op.drop_table("reviews")
    op.drop_table("edition_authors")
    op.drop_table("reviewers")
    op.drop_table("editions")
    op.drop_table("books")
    op.drop_table("authors")
