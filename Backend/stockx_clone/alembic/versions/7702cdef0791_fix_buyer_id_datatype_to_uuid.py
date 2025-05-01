"""fix buyer_id datatype to UUID

Revision ID: 7702cdef0791
Revises: 356b51a9e56f
Create Date: 2025-04-28 23:38:28.574233

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7702cdef0791'
down_revision: Union[str, None] = '356b51a9e56f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
