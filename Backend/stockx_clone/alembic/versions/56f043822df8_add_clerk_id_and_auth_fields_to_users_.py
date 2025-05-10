"""Add clerk_id and auth fields to users table

Revision ID: 56f043822df8
Revises: 1d50c13bc34c
Create Date: 2025-05-08 23:48:47.989708

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '56f043822df8'
down_revision: Union[str, None] = '1d50c13bc34c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
