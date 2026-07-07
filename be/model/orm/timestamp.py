from __future__ import annotations
import uuid
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from model.orm.base import Base


class TimeStamp(Base):
    __tablename__ = "timestamps"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    value: Mapped[dict] = mapped_column(JSONB, nullable=False)
    data_series_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("data_series.id", ondelete="CASCADE"), nullable=False
    )

    data_series: Mapped["DataSeries"] = relationship("DataSeries", back_populates="timestamps")  # noqa: F821

    __table_args__ = (
        Index("ix_timestamps_data_series_id_date", "data_series_id", "date"),
    )
