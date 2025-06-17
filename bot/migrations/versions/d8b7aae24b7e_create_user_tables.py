"""Create user tables

Revision ID: d8b7aae24b7e
Revises:
Create Date: 2025-06-17 17:33:06.075578

"""

from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "d8b7aae24b7e"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
