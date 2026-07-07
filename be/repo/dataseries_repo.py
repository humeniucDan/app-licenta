import uuid
from sqlalchemy.orm import Session, selectinload

from model.orm.dataseries import DataSeries
from model.orm.timestamp import TimeStamp


class DataSeriesRepo:
    @staticmethod
    def get_with_timestamps(db: Session, id: uuid.UUID):
        return (
            db.query(DataSeries)
            .options(selectinload(DataSeries.timestamps))
            .filter(DataSeries.id == id)
            .first()
        )
