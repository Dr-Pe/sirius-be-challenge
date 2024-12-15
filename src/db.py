from typing import Annotated
from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine, select
from models.settings import SETTINGS
import models

sqlite_url = f"sqlite:///{SETTINGS.sqlite_filename}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def insert_model_instance(model: SQLModel):
    with Session(engine) as session:
        session.add(model)
        session.commit()
        session.refresh(model)


def get_db_user(username: str):
    with Session(engine) as session:
        return session.exec(select(models.User).where(models.User.username == username)).first()


def get_db_users():
    with Session(engine) as session:
        return session.exec(select(models.User)).all()


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
