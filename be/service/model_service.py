import uuid
from sqlalchemy.orm import Session

from model.orm.model import Model
from model.schema.model import ModelCreate, ModelRead, ModelDetailRead
from repo.model_repo import ModelRepo
from repo.base_repo import get, get_all, create, delete
from util.exceptions import NotFoundError


class ModelService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[ModelRead]:
        return [ModelRead.model_validate(m) for m in get_all(self.db, Model)]

    def get(self, id: uuid.UUID) -> ModelRead:
        model = get(self.db, Model, id)
        if not model:
            raise NotFoundError("Model not found")
        return ModelRead.model_validate(model)

    def get_detail(self, id: uuid.UUID) -> ModelDetailRead:
        model = ModelRepo.get_with_series(self.db, id)
        if not model:
            raise NotFoundError("Model not found")
        return ModelDetailRead.model_validate(model)

    def create(self, data: ModelCreate) -> ModelRead:
        model = create(self.db, Model, name=data.name)
        self.db.commit()
        return ModelRead.model_validate(model)

    def delete(self, id: uuid.UUID) -> None:
        model = get(self.db, Model, id)
        if not model:
            raise NotFoundError("Model not found")
        delete(self.db, model)
        self.db.commit()
