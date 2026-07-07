from __future__ import annotations
import uuid
from pydantic import BaseModel, ConfigDict


class EvaluationCreate(BaseModel):
    metric_id: uuid.UUID
    true_data_series_id: uuid.UUID
    pred_data_series_id: uuid.UUID
    value: float


class EvaluationRead(BaseModel):
    id: uuid.UUID
    metric_id: uuid.UUID
    true_data_series_id: uuid.UUID
    pred_data_series_id: uuid.UUID
    value: float

    model_config = ConfigDict(from_attributes=True)
