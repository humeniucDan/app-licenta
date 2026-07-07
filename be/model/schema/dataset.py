from __future__ import annotations
import uuid
from pydantic import BaseModel, ConfigDict

from model.schema.dataseries import DataSeriesWithTimestampsRead


class DataSetCreate(BaseModel):
    name: str
    description: str | None = None


class DataSetRead(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None

    model_config = ConfigDict(from_attributes=True)


class DataSetDetailRead(DataSetRead):
    data_series: list[DataSeriesWithTimestampsRead] = []
