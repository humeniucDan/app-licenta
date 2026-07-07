from __future__ import annotations
import uuid
from sqlalchemy import Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from model.orm.base import Base


class Evaluation(Base):
    __tablename__ = "evaluations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    metric_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("metrics.id", ondelete="RESTRICT"), nullable=False
    )
    true_data_series_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("data_series.id", ondelete="RESTRICT"), nullable=False
    )
    pred_data_series_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("data_series.id", ondelete="RESTRICT"), nullable=False
    )
    value: Mapped[float] = mapped_column(Float, nullable=False)

    metric: Mapped["Metric"] = relationship("Metric", back_populates="evaluations")  # noqa: F821
    true_data_series: Mapped["DataSeries"] = relationship(  # noqa: F821
        "DataSeries", foreign_keys=[true_data_series_id], back_populates="true_evaluations"
    )
    pred_data_series: Mapped["DataSeries"] = relationship(  # noqa: F821
        "DataSeries", foreign_keys=[pred_data_series_id], back_populates="pred_evaluations"
    )
