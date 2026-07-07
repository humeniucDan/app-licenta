from __future__ import annotations
import uuid
from pydantic import BaseModel, ConfigDict


class MetricCreate(BaseModel):
    name: str
    description: str | None = None


class MetricRead(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None

    model_config = ConfigDict(from_attributes=True)
