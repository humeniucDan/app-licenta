import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from model.schema.timestamp import TimeStampCreate, TimeStampRead
from service.timestamp_service import TimeStampService

router = APIRouter(prefix="/timestamps", tags=["timestamps"])


@router.get("")
def list_timestamps(db: Session = Depends(get_db)) -> list[TimeStampRead]:
    return TimeStampService(db).get_all()


@router.post("")
def create_timestamp(data: TimeStampCreate, db: Session = Depends(get_db)) -> TimeStampRead:
    return TimeStampService(db).create(data)


@router.get("/{id}")
def get_timestamp(id: uuid.UUID, db: Session = Depends(get_db)) -> TimeStampRead:
    return TimeStampService(db).get(id)


@router.delete("/{id}")
def delete_timestamp(id: uuid.UUID, db: Session = Depends(get_db)):
    TimeStampService(db).delete(id)
