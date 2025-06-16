"""adding nullable

Revision ID: a7cdf30c8d34
Revises: 1d1c6dae4e94
Create Date: 2025-06-17 02:11:15.705403

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "a7cdf30c8d34"
down_revision: Union[str, None] = "1d1c6dae4e94"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column("users", "email", nullable=True)
    op.alter_column("users", "cloud_primary_key", nullable=True)
    op.alter_column("users", "cloud_secondary_key", nullable=True)
    op.alter_column("users", "cloud_third_key", nullable=True)


def downgrade():
    op.alter_column("users", "email", nullable=False)
    op.alter_column("users", "cloud_primary_key", nullable=False)
    op.alter_column("users", "cloud_secondary_key", nullable=False)
    op.alter_column("users", "cloud_third_key", nullable=False)
