"""adiciona error_screenshot em crawl_jobs

Revision ID: 002
Revises: 001
Create Date: 2026-02-18 00:35:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: str | None = '001'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Adiciona coluna error_screenshot (LargeBinary/BYTEA)
    op.add_column('crawl_jobs', sa.Column('error_screenshot', sa.LargeBinary(), nullable=True))


def downgrade() -> None:
    op.drop_column('crawl_jobs', 'error_screenshot')
