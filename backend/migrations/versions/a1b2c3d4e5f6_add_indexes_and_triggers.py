"""Add indexes and updated_at trigger.

Revision ID: a1b2c3d4e5f6
Revises: 0d6439d2e79f
Create Date: 2026-04-20 12:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "0d6439d2e79f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index("ix_files_created_at", "files", ["created_at"])
    op.create_index("ix_alerts_file_id", "alerts", ["file_id"])
    op.create_index("ix_alerts_created_at", "alerts", ["created_at"])

    op.alter_column(
        "files",
        "scan_details",
        type_=sa.String(1000),
        existing_nullable=True,
    )

    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE 'plpgsql';
    """)

    op.execute("""
        CREATE TRIGGER trigger_files_updated_at
            BEFORE UPDATE ON files
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trigger_files_updated_at ON files;")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column;")

    op.alter_column(
        "files",
        "scan_details",
        type_=sa.String(500),
        existing_nullable=True,
    )

    op.drop_index("ix_alerts_created_at", table_name="alerts")
    op.drop_index("ix_alerts_file_id", table_name="alerts")
    op.drop_index("ix_files_created_at", table_name="files")
