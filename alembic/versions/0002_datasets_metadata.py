"""datasets metadata foundation

Revision ID: 0002_datasets_metadata
Revises: 0001_initial_schema
Create Date: 2026-03-03 00:30:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0002_datasets_metadata"
down_revision: str | None = "0001_initial_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "datasets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("file_path", sa.String(length=1024), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("row_count", sa.Integer(), nullable=False),
        sa.Column("column_count", sa.Integer(), nullable=False),
        sa.Column("uploaded_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("organization_id", "name", name="uq_datasets_org_name"),
    )
    op.create_index(op.f("ix_datasets_organization_id"), "datasets", ["organization_id"], unique=False)
    op.create_index(op.f("ix_datasets_uploaded_by"), "datasets", ["uploaded_by"], unique=False)

    op.create_table(
        "dataset_columns",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("dataset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("data_type", sa.String(length=32), nullable=False),
        sa.Column("has_missing_values", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("unique_values_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["dataset_id"], ["datasets.id"], ondelete="CASCADE"),
    )
    op.create_index(op.f("ix_dataset_columns_dataset_id"), "dataset_columns", ["dataset_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_dataset_columns_dataset_id"), table_name="dataset_columns")
    op.drop_table("dataset_columns")

    op.drop_index(op.f("ix_datasets_uploaded_by"), table_name="datasets")
    op.drop_index(op.f("ix_datasets_organization_id"), table_name="datasets")
    op.drop_table("datasets")
