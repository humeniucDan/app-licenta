import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from model.schema.dataset import DataSetCreate, DataSetRead, DataSetDetailRead
from service.dataset_service import DataSetService

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.get("")
def list_datasets(db: Session = Depends(get_db)) -> list[DataSetRead]:
    return DataSetService(db).get_all()


@router.post("")
def create_dataset(data: DataSetCreate, db: Session = Depends(get_db)) -> DataSetRead:
    return DataSetService(db).create(data)


@router.get("/{id}")
def get_dataset(id: uuid.UUID, db: Session = Depends(get_db)) -> DataSetDetailRead:
    return DataSetService(db).get_detail(id)


@router.delete("/{id}")
def delete_dataset(id: uuid.UUID, db: Session = Depends(get_db)):
    DataSetService(db).delete(id)
