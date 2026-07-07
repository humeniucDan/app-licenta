import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from model.schema.model import ModelCreate, ModelRead, ModelDetailRead
from service.model_service import ModelService

router = APIRouter(prefix="/models", tags=["models"])


@router.get("")
def list_models(db: Session = Depends(get_db)) -> list[ModelRead]:
    return ModelService(db).get_all()


@router.post("")
def create_model(data: ModelCreate, db: Session = Depends(get_db)) -> ModelRead:
    return ModelService(db).create(data)


@router.get("/{id}")
def get_model(id: uuid.UUID, db: Session = Depends(get_db)) -> ModelDetailRead:
    return ModelService(db).get_detail(id)


@router.delete("/{id}")
def delete_model(id: uuid.UUID, db: Session = Depends(get_db)):
    ModelService(db).delete(id)
