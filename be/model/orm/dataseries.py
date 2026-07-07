from __future__ import annotations
import uuid
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from model.orm.base import Base


class DataSeries(Base):
    __tablename__ = "data_series"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_model_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("models.id", ondelete="RESTRICT"), nullable=True
    )
    data_set_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("data_sets.id", ondelete="RESTRICT"), nullable=False
    )

    source_model: Mapped["Model"] = relationship("Model", back_populates="data_series")  # noqa: F821
    data_set: Mapped["DataSet"] = relationship("DataSet", back_populates="data_series")  # noqa: F821
    timestamps: Mapped[list["TimeStamp"]] = relationship("TimeStamp", back_populates="data_series")  # noqa: F821
    true_evaluations: Mapped[list["Evaluation"]] = relationship(  # noqa: F821
        "Evaluation", foreign_keys="Evaluation.true_data_series_id", back_populates="true_data_series"
    )
    pred_evaluations: Mapped[list["Evaluation"]] = relationship(  # noqa: F821
        "Evaluation", foreign_keys="Evaluation.pred_data_series_id", back_populates="pred_data_series"
    )
