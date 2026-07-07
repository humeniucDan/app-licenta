import uuid
from sqlalchemy.orm import Session

from model.orm.timestamp import TimeStamp
from model.orm.dataseries import DataSeries
from model.schema.timestamp import TimeStampCreate, TimeStampRead
from repo.base_repo import get, get_all, create, delete
from util.exceptions import NotFoundError


class TimeStampService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[TimeStampRead]:
        return [TimeStampRead.model_validate(ts) for ts in get_all(self.db, TimeStamp)]

    def get(self, id: uuid.UUID) -> TimeStampRead:
        ts = get(self.db, TimeStamp, id)
        if not ts:
            raise NotFoundError("TimeStamp not found")
        return TimeStampRead.model_validate(ts)

    def create(self, data: TimeStampCreate) -> TimeStampRead:
        if not get(self.db, DataSeries, data.data_series_id):
            raise NotFoundError("DataSeries not found")
        ts = create(
            self.db, TimeStamp,
            date=data.date,
            value=data.value,
            data_series_id=data.data_series_id,
        )
        self.db.commit()
        return TimeStampRead.model_validate(ts)

    def delete(self, id: uuid.UUID) -> None:
        ts = get(self.db, TimeStamp, id)
        if not ts:
            raise NotFoundError("TimeStamp not found")
        delete(self.db, ts)
        self.db.commit()
