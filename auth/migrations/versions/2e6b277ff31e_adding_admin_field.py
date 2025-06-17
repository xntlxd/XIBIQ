"""adding admin field

Revision ID: 2e6b277ff31e
Revises: a7cdf30c8d34
Create Date: 2025-06-17 19:08:23.354427

"""

from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "2e6b277ff31e"
down_revision: Union[str, None] = "a7cdf30c8d34"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
