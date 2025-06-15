"""Change User Model

Revision ID: da6f5959263a
Revises: 56f043822df8
Create Date: 2025-05-23 13:32:32.001304

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'da6f5959263a'
down_revision: Union[str, None] = '56f043822df8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
