import uuid
from sqlalchemy.orm import Session

from model.orm.dataseries import DataSeries
from model.orm.dataset import DataSet
from model.orm.model import Model
from model.schema.dataseries import DataSeriesCreate, DataSeriesRead, DataSeriesWithTimestampsRead
from repo.dataseries_repo import DataSeriesRepo
from repo.base_repo import get, get_all, create, delete
from util.exceptions import NotFoundError


class DataSeriesService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[DataSeriesRead]:
        return [DataSeriesRead.model_validate(ds) for ds in get_all(self.db, DataSeries)]

    def get(self, id: uuid.UUID) -> DataSeriesRead:
        ds = get(self.db, DataSeries, id)
        if not ds:
            raise NotFoundError("DataSeries not found")
        return DataSeriesRead.model_validate(ds)

    def get_with_timestamps(self, id: uuid.UUID) -> DataSeriesWithTimestampsRead:
        ds = DataSeriesRepo.get_with_timestamps(self.db, id)
        if not ds:
            raise NotFoundError("DataSeries not found")
        return DataSeriesWithTimestampsRead.model_validate(ds)

    def create(self, data: DataSeriesCreate) -> DataSeriesRead:
        if not get(self.db, DataSet, data.data_set_id):
            raise NotFoundError("DataSet not found")
        if data.source_model_id and not get(self.db, Model, data.source_model_id):
            raise NotFoundError("Model not found")
        ds = create(
            self.db, DataSeries,
            name=data.name,
            data_set_id=data.data_set_id,
            source_model_id=data.source_model_id,
        )
        self.db.commit()
        return DataSeriesRead.model_validate(ds)

    def delete(self, id: uuid.UUID) -> None:
        ds = get(self.db, DataSeries, id)
        if not ds:
            raise NotFoundError("DataSeries not found")
        delete(self.db, ds)
        self.db.commit()
