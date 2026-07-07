import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from model.schema.metric import MetricCreate, MetricRead
from service.metric_service import MetricService

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("")
def list_metrics(db: Session = Depends(get_db)) -> list[MetricRead]:
    return MetricService(db).get_all()


@router.post("")
def create_metric(data: MetricCreate, db: Session = Depends(get_db)) -> MetricRead:
    return MetricService(db).create(data)


@router.get("/{id}")
def get_metric(id: uuid.UUID, db: Session = Depends(get_db)) -> MetricRead:
    return MetricService(db).get(id)


@router.delete("/{id}")
def delete_metric(id: uuid.UUID, db: Session = Depends(get_db)):
    MetricService(db).delete(id)
