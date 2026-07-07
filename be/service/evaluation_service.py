import uuid
from sqlalchemy.orm import Session

from model.orm.evaluation import Evaluation
from model.orm.metric import Metric
from model.orm.dataseries import DataSeries
from model.schema.evaluation import EvaluationCreate, EvaluationRead
from repo.base_repo import get, get_all, create, delete
from util.exceptions import NotFoundError


class EvaluationService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[EvaluationRead]:
        return [EvaluationRead.model_validate(e) for e in get_all(self.db, Evaluation)]

    def get(self, id: uuid.UUID) -> EvaluationRead:
        e = get(self.db, Evaluation, id)
        if not e:
            raise NotFoundError("Evaluation not found")
        return EvaluationRead.model_validate(e)

    def create(self, data: EvaluationCreate) -> EvaluationRead:
        if not get(self.db, Metric, data.metric_id):
            raise NotFoundError("Metric not found")
        if not get(self.db, DataSeries, data.true_data_series_id):
            raise NotFoundError("DataSeries (true) not found")
        if not get(self.db, DataSeries, data.pred_data_series_id):
            raise NotFoundError("DataSeries (pred) not found")
        e = create(
            self.db, Evaluation,
            metric_id=data.metric_id,
            true_data_series_id=data.true_data_series_id,
            pred_data_series_id=data.pred_data_series_id,
            value=data.value,
        )
        return EvaluationRead.model_validate(e)

    def delete(self, id: uuid.UUID) -> None:
        e = get(self.db, Evaluation, id)
        if not e:
            raise NotFoundError("Evaluation not found")
        delete(self.db, e)
