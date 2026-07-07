from __future__ import annotations
import uuid
from pydantic import BaseModel, ConfigDict

from model.schema.timestamp import TimeStampRead


class DataSeriesCreate(BaseModel):
    name: str
    data_set_id: uuid.UUID
    source_model_id: uuid.UUID | None = None


class DataSeriesRead(BaseModel):
    id: uuid.UUID
    name: str
    source_model_id: uuid.UUID | None
    data_set_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


class DataSeriesWithTimestampsRead(DataSeriesRead):
    timestamps: list[TimeStampRead] = []
