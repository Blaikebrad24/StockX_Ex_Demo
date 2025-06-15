"""Change User Model again

Revision ID: 876d133fb507
Revises: da6f5959263a
Create Date: 2025-05-23 13:41:51.700949

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '876d133fb507'
down_revision: Union[str, None] = 'da6f5959263a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
