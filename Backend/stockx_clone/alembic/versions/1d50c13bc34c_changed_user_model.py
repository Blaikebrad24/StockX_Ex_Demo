"""Changed user model

Revision ID: 1d50c13bc34c
Revises: 7702cdef0791
Create Date: 2025-05-08 18:48:27.992334

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1d50c13bc34c'
down_revision: Union[str, None] = '7702cdef0791'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
