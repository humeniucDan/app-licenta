import uuid
from sqlalchemy.orm import Session

from model.orm.metric import Metric
from model.schema.metric import MetricCreate, MetricRead
from repo.base_repo import get, get_all, create, delete
from util.exceptions import NotFoundError


class MetricService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[MetricRead]:
        return [MetricRead.model_validate(m) for m in get_all(self.db, Metric)]

    def get(self, id: uuid.UUID) -> MetricRead:
        m = get(self.db, Metric, id)
        if not m:
            raise NotFoundError("Metric not found")
        return MetricRead.model_validate(m)

    def create(self, data: MetricCreate) -> MetricRead:
        m = create(self.db, Metric, name=data.name, description=data.description)
        self.db.commit()
        return MetricRead.model_validate(m)

    def delete(self, id: uuid.UUID) -> None:
        m = get(self.db, Metric, id)
        if not m:
            raise NotFoundError("Metric not found")
        delete(self.db, m)
        self.db.commit()
