import uuid
from sqlalchemy.orm import Session, selectinload

from model.orm.model import Model


class ModelRepo:
    @staticmethod
    def get_with_series(db: Session, id: uuid.UUID):
        return (
            db.query(Model)
            .options(selectinload(Model.data_series))
            .filter(Model.id == id)
            .first()
        )
