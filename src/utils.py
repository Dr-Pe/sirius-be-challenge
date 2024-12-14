from fastapi import HTTPException

import models
from db import get_user, insert_model_instance
from file_storage_client import FileStorageClient
from security import get_password_hash


def create_user(user: models.User, fs_client: FileStorageClient):
    if get_user(user.username):
        raise HTTPException(status_code=400, detail="User already exists")

    user_in_db = models.User(
        username=user.username,
        password=get_password_hash(user.password),
        is_admin=user.is_admin,
    )
    insert_model_instance(user_in_db)
    fs_client.create_bucket(user.username)

    return user
