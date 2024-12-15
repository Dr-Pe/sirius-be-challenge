from fastapi import HTTPException
from sqlmodel import Session, update
import models
from db import engine, get_db_user, insert_model_instance
from file_storage_client import FileStorageClient
from models.settings import SETTINGS
from security import get_password_hash


def create_user(user_dto: models.CreateUserDTO, fs_client: FileStorageClient):
    if get_db_user(user_dto.username):
        raise HTTPException(status_code=400, detail="User already exists")

    user_in_db = models.User(
        username=user_dto.username,
        password=get_password_hash(user_dto.password),
        is_admin=user_dto.is_admin,
    )
    insert_model_instance(user_in_db)
    fs_client.create_bucket(user_dto.username)

    return user_dto


class UserManager:

    def __init__(self, user: models.User):
        self.user = user

    def can_upload_file(self):
        return self.user.quota < SETTINGS.max_quota_in_gb

    def update_user_quota(self, new_quota: float):
        with Session(engine) as session:
            session.exec(update(models.User).where(
                models.User.username == self.user.username).values(quota=new_quota))
            session.commit()

        return new_quota
