from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine, select
from settings import SETTINGS

import models

sqlite_url = f"sqlite:///{SETTINGS.sqlite_file_name}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


def get_user(session: SessionDep, username: str):
    return session.exec(select(models.User).where(models.User.username == username)).first()
