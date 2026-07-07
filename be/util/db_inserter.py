import uuid
from sqlalchemy.orm import Session

from model.orm.model import Model
from model.orm.dataset import DataSet
from model.orm.dataseries import DataSeries
from model.orm.timestamp import TimeStamp
from model.orm.metric import Metric
from model.orm.evaluation import Evaluation
from repo.base_repo import create


class DBInserter:
    def __init__(self, db: Session):
        self.db = db

    def insert_model(self, name: str) -> Model:
        return create(self.db, Model, name=name)

    def insert_dataset(self, name: str, description: str | None = None) -> DataSet:
        return create(self.db, DataSet, name=name, description=description)

    def insert_dataseries(
        self, name: str, data_set_id: uuid.UUID, source_model_id: uuid.UUID | None = None
    ) -> DataSeries:
        return create(
            self.db, DataSeries,
            name=name,
            data_set_id=data_set_id,
            source_model_id=source_model_id,
        )

    def insert_timestamps_bulk(
        self, data_series_id: uuid.UUID, records: list[dict]
    ) -> int:
        from sqlalchemy import insert

        for r in records:
            r["data_series_id"] = data_series_id
        self.db.execute(insert(TimeStamp), records)
        return len(records)

    def insert_metric(self, name: str, description: str | None = None) -> Metric:
        return create(self.db, Metric, name=name, description=description)

    def insert_evaluation(
        self,
        metric_id: uuid.UUID,
        true_data_series_id: uuid.UUID,
        pred_data_series_id: uuid.UUID,
        value: float,
    ) -> Evaluation:
        return create(
            self.db, Evaluation,
            metric_id=metric_id,
            true_data_series_id=true_data_series_id,
            pred_data_series_id=pred_data_series_id,
            value=value,
        )
