import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from model.schema.evaluation import EvaluationCreate, EvaluationRead
from service.evaluation_service import EvaluationService

router = APIRouter(prefix="/evaluations", tags=["evaluations"])


@router.get("")
def list_evaluations(db: Session = Depends(get_db)) -> list[EvaluationRead]:
    return EvaluationService(db).get_all()


@router.post("")
def create_evaluation(data: EvaluationCreate, db: Session = Depends(get_db)) -> EvaluationRead:
    return EvaluationService(db).create(data)


@router.get("/{id}")
def get_evaluation(id: uuid.UUID, db: Session = Depends(get_db)) -> EvaluationRead:
    return EvaluationService(db).get(id)


@router.delete("/{id}")
def delete_evaluation(id: uuid.UUID, db: Session = Depends(get_db)):
    EvaluationService(db).delete(id)
