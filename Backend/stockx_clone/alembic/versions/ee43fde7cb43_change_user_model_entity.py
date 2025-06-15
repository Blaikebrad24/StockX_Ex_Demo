"""Change User Model entity

Revision ID: ee43fde7cb43
Revises: 297aac634579
Create Date: 2025-05-23 13:49:29.043840

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ee43fde7cb43'
down_revision: Union[str, None] = '297aac634579'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
