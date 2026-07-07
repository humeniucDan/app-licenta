"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-07-06
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "models",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False),
    )
    op.create_table(
        "data_sets",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
    )
    op.create_table(
        "data_series",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("source_model_id", UUID(as_uuid=True), sa.ForeignKey("models.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("data_set_id", UUID(as_uuid=True), sa.ForeignKey("data_sets.id", ondelete="RESTRICT"), nullable=False),
    )
    op.create_index(op.f("ix_data_series_source_model_id"), "data_series", ["source_model_id"])
    op.create_index(op.f("ix_data_series_data_set_id"), "data_series", ["data_set_id"])
    op.create_table(
        "timestamps",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, default=sa.text("gen_random_uuid()")),
        sa.Column("date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("value", JSONB, nullable=False),
        sa.Column("data_series_id", UUID(as_uuid=True), sa.ForeignKey("data_series.id", ondelete="CASCADE"), nullable=False),
    )
    op.create_index(op.f("ix_timestamps_data_series_id"), "timestamps", ["data_series_id"])
    op.create_index("ix_timestamps_data_series_id_date", "timestamps", ["data_series_id", "date"])
    op.create_table(
        "metrics",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
    )
    op.create_table(
        "evaluations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, default=sa.text("gen_random_uuid()")),
        sa.Column("metric_id", UUID(as_uuid=True), sa.ForeignKey("metrics.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("true_data_series_id", UUID(as_uuid=True), sa.ForeignKey("data_series.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("pred_data_series_id", UUID(as_uuid=True), sa.ForeignKey("data_series.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
    )
    op.create_index(op.f("ix_evaluations_metric_id"), "evaluations", ["metric_id"])
    op.create_index(op.f("ix_evaluations_true_data_series_id"), "evaluations", ["true_data_series_id"])
    op.create_index(op.f("ix_evaluations_pred_data_series_id"), "evaluations", ["pred_data_series_id"])


def downgrade() -> None:
    op.drop_table("evaluations")
    op.drop_table("metrics")
    op.drop_table("timestamps")
    op.drop_table("data_series")
    op.drop_table("data_sets")
    op.drop_table("models")
