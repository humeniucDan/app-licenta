import uuid
from sqlalchemy.orm import Session


def get(db: Session, model_class, id: uuid.UUID):
    return db.query(model_class).filter(model_class.id == id).first()


def get_all(db: Session, model_class):
    return db.query(model_class).all()


def create(db: Session, model_class, **kwargs):
    obj = model_class(**kwargs)
    db.add(obj)
    db.flush()
    return obj


def delete(db: Session, obj):
    db.delete(obj)
    db.flush()
