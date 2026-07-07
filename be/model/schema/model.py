from __future__ import annotations
import uuid
from pydantic import BaseModel, ConfigDict

from model.schema.dataseries import DataSeriesRead


class ModelCreate(BaseModel):
    name: str


class ModelRead(BaseModel):
    id: uuid.UUID
    name: str

    model_config = ConfigDict(from_attributes=True)


class ModelDetailRead(ModelRead):
    data_series: list[DataSeriesRead] = []
