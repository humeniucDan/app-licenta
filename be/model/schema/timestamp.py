from __future__ import annotations
import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class TimeStampCreate(BaseModel):
    date: datetime
    value: dict
    data_series_id: uuid.UUID


class TimeStampRead(BaseModel):
    id: uuid.UUID
    date: datetime
    value: dict
    data_series_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)
