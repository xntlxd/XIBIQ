"""adding admin field second try

Revision ID: 21be1733e0f7
Revises: 2e6b277ff31e
Create Date: 2025-06-17 19:12:22.052487

"""

from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "21be1733e0f7"
down_revision: Union[str, None] = "2e6b277ff31e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
