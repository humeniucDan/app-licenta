from __future__ import annotations
import uuid
from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from model.orm.base import Base


class DataSet(Base):
    __tablename__ = "data_sets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    data_series: Mapped[list["DataSeries"]] = relationship("DataSeries", back_populates="data_set")  # noqa: F821
