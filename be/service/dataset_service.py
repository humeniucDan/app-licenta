import uuid
from sqlalchemy.orm import Session

from model.orm.dataset import DataSet
from model.schema.dataset import DataSetCreate, DataSetRead, DataSetDetailRead
from repo.dataset_repo import DataSetRepo
from repo.base_repo import get, get_all, create, delete
from util.exceptions import NotFoundError


class DataSetService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[DataSetRead]:
        return [DataSetRead.model_validate(ds) for ds in get_all(self.db, DataSet)]

    def get(self, id: uuid.UUID) -> DataSetRead:
        ds = get(self.db, DataSet, id)
        if not ds:
            raise NotFoundError("DataSet not found")
        return DataSetRead.model_validate(ds)

    def get_detail(self, id: uuid.UUID) -> DataSetDetailRead:
        ds = DataSetRepo.get_with_series_and_timestamps(self.db, id)
        if not ds:
            raise NotFoundError("DataSet not found")
        return DataSetDetailRead.model_validate(ds)

    def create(self, data: DataSetCreate) -> DataSetRead:
        ds = create(self.db, DataSet, name=data.name, description=data.description)
        return DataSetRead.model_validate(ds)

    def delete(self, id: uuid.UUID) -> None:
        ds = get(self.db, DataSet, id)
        if not ds:
            raise NotFoundError("DataSet not found")
        delete(self.db, ds)
