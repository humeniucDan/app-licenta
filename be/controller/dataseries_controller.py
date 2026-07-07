import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from model.schema.dataseries import DataSeriesCreate, DataSeriesRead, DataSeriesWithTimestampsRead
from service.dataseries_service import DataSeriesService

router = APIRouter(prefix="/dataseries", tags=["dataseries"])


@router.get("")
def list_dataseries(db: Session = Depends(get_db)) -> list[DataSeriesRead]:
    return DataSeriesService(db).get_all()


@router.post("")
def create_dataseries(data: DataSeriesCreate, db: Session = Depends(get_db)) -> DataSeriesRead:
    return DataSeriesService(db).create(data)


@router.get("/{id}")
def get_dataseries(id: uuid.UUID, db: Session = Depends(get_db)) -> DataSeriesWithTimestampsRead:
    return DataSeriesService(db).get_with_timestamps(id)


@router.delete("/{id}")
def delete_dataseries(id: uuid.UUID, db: Session = Depends(get_db)):
    DataSeriesService(db).delete(id)
