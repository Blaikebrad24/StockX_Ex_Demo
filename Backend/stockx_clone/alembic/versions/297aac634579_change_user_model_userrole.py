"""Change User Model userRole

Revision ID: 297aac634579
Revises: 876d133fb507
Create Date: 2025-05-23 13:46:11.381460

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '297aac634579'
down_revision: Union[str, None] = '876d133fb507'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
