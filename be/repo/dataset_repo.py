import uuid
from sqlalchemy.orm import Session, selectinload

from model.orm.dataset import DataSet
from model.orm.dataseries import DataSeries
from model.orm.timestamp import TimeStamp


class DataSetRepo:
    @staticmethod
    def get_with_series_and_timestamps(db: Session, id: uuid.UUID):
        return (
            db.query(DataSet)
            .options(selectinload(DataSet.data_series).selectinload(DataSeries.timestamps))
            .filter(DataSet.id == id)
            .first()
        )
