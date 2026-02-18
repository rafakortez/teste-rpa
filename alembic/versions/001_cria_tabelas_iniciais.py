"""cria tabelas iniciais

Revision ID: 001
Revises:
Create Date: 2026-02-17
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "crawl_jobs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("job_type", sa.String(), nullable=False),
        sa.Column("status", sa.String(), server_default="pending", nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "hockey_teams",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("job_id", sa.String(), sa.ForeignKey("crawl_jobs.id"), nullable=False),
        sa.Column("team_name", sa.String(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("wins", sa.Integer(), nullable=True),
        sa.Column("losses", sa.Integer(), nullable=True),
        sa.Column("ot_losses", sa.Integer(), nullable=True),
        sa.Column("win_pct", sa.Float(), nullable=True),
        sa.Column("goals_for", sa.Integer(), nullable=True),
        sa.Column("goals_against", sa.Integer(), nullable=True),
        sa.Column("goal_diff", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "oscar_films",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("job_id", sa.String(), sa.ForeignKey("crawl_jobs.id"), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("nominations", sa.Integer(), nullable=False),
        sa.Column("awards", sa.Integer(), nullable=False),
        sa.Column("best_picture", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("oscar_films")
    op.drop_table("hockey_teams")
    op.drop_table("crawl_jobs")
